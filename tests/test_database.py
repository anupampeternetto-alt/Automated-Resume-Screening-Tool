import sqlite3
import json
from pathlib import Path

import pytest


SCHEMA_PATH = (
    Path(__file__).resolve().parents[1]
    / "db"
    / "schema.sql"
)


@pytest.fixture
def db():
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row

    connection.executescript(
        SCHEMA_PATH.read_text(encoding="utf-8-sig")
    )

    yield connection

    connection.close()


def test_schema_creation(db):
    tables = {
        row[0]
        for row in db.execute(
            "SELECT name FROM sqlite_master "
            "WHERE type='table'"
        )
    }

    assert tables == {
        "jobs",
        "candidates",
        "resumes",
        "features",
        "rankings",
    }


def test_primary_keys(db):
    db.execute(
        "INSERT INTO candidates(id, name) VALUES (?, ?)",
        ("C001", "Candidate A"),
    )

    with pytest.raises(sqlite3.IntegrityError):
        db.execute(
            "INSERT INTO candidates(id, name) VALUES (?, ?)",
            ("C001", "Duplicate Candidate"),
        )


def test_foreign_key_enforcement(db):
    assert db.execute(
        "PRAGMA foreign_keys"
    ).fetchone()[0] == 1

    with pytest.raises(sqlite3.IntegrityError):
        db.execute(
            "INSERT INTO resumes "
            "(candidate_id, source, raw_text) "
            "VALUES (?, ?, ?)",
            ("INVALID", "test.txt", "Python"),
        )


def test_valid_json_storage(db):
    skills = ["Python", "SQL"]

    db.execute(
        "INSERT INTO jobs "
        "(id, title, jd_text, must_have) "
        "VALUES (?, ?, ?, ?)",
        (
            "J001",
            "Python Developer",
            "Python and SQL required",
            json.dumps(skills),
        ),
    )

    result = db.execute(
        "SELECT must_have FROM jobs WHERE id=?",
        ("J001",),
    ).fetchone()[0]

    assert json.loads(result) == skills


def test_invalid_json_rejection(db):
    with pytest.raises(sqlite3.IntegrityError):
        db.execute(
            "INSERT INTO jobs "
            "(id, title, jd_text, must_have) "
            "VALUES (?, ?, ?, ?)",
            ("J001", "Developer", "Test", "INVALID_JSON"),
        )


def test_crud_operations(db):
    db.execute(
        "INSERT INTO candidates(id, name) VALUES (?, ?)",
        ("C001", "Candidate A"),
    )

    result = db.execute(
        "SELECT name FROM candidates WHERE id=?",
        ("C001",),
    ).fetchone()

    assert result[0] == "Candidate A"

    db.execute(
        "UPDATE candidates SET name=? WHERE id=?",
        ("Updated Candidate", "C001"),
    )

    result = db.execute(
        "SELECT name FROM candidates WHERE id=?",
        ("C001",),
    ).fetchone()

    assert result[0] == "Updated Candidate"

    db.execute(
        "DELETE FROM candidates WHERE id=?",
        ("C001",),
    )

    assert db.execute(
        "SELECT COUNT(*) FROM candidates"
    ).fetchone()[0] == 0


def test_cascade_delete(db):
    db.execute(
        "INSERT INTO candidates(id, name) VALUES (?, ?)",
        ("C001", "Candidate A"),
    )

    db.execute(
        "INSERT INTO resumes "
        "(candidate_id, source, raw_text) "
        "VALUES (?, ?, ?)",
        ("C001", "resume.txt", "Python SQL"),
    )

    assert db.execute(
        "SELECT COUNT(*) FROM resumes"
    ).fetchone()[0] == 1

    db.execute(
        "DELETE FROM candidates WHERE id=?",
        ("C001",),
    )

    assert db.execute(
        "SELECT COUNT(*) FROM resumes"
    ).fetchone()[0] == 0


def test_ranking_and_joins(db):
    db.execute(
        "INSERT INTO jobs(id, title, jd_text) "
        "VALUES (?, ?, ?)",
        ("J001", "Python Developer", "Python SQL"),
    )

    candidates = [
        ("C001", "Candidate A", 90.0),
        ("C002", "Candidate B", 75.0),
        ("C003", "Candidate C", 25.0),
    ]

    for candidate_id, name, score in candidates:
        db.execute(
            "INSERT INTO candidates(id, name) VALUES (?, ?)",
            (candidate_id, name),
        )

        db.execute(
            "INSERT INTO rankings "
            "(job_id, candidate_id, score, reasons) "
            "VALUES (?, ?, ?, ?)",
            (
                "J001",
                candidate_id,
                score,
                json.dumps({"synthetic": True}),
            ),
        )

    rows = db.execute(
        """
        SELECT j.title, c.name, r.score
        FROM rankings r
        JOIN jobs j ON r.job_id = j.id
        JOIN candidates c ON r.candidate_id = c.id
        ORDER BY r.score DESC
        """
    ).fetchall()

    assert len(rows) == 3
    assert [row["score"] for row in rows] == [
        90.0, 75.0, 25.0
    ]
    assert rows[0]["name"] == "Candidate A"
    assert rows[0]["title"] == "Python Developer"


def test_check_constraints(db):
    with pytest.raises(sqlite3.IntegrityError):
        db.execute(
            "INSERT INTO jobs "
            "(id, title, jd_text, min_exp_years) "
            "VALUES (?, ?, ?, ?)",
            ("J001", "Developer", "Test", -1),
        )


def test_database_integrity(db):
    result = db.execute(
        "PRAGMA integrity_check"
    ).fetchone()[0]

    violations = db.execute(
        "PRAGMA foreign_key_check"
    ).fetchall()

    assert result == "ok"
    assert violations == []