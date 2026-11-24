import json
from pathlib import Path

import pytest

import src.database as db
from src.ingest import ingest_resume, ingest_folder


RESUMES = Path(__file__).resolve().parents[1] / "resumes"


@pytest.fixture(autouse=True)
def temporary_database(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DB_PATH", tmp_path / "test.db")
    db.initialize_database()


def count_records(table):
    connection = db.get_connection()

    try:
        return connection.execute(
            f"SELECT COUNT(*) FROM {table}"
        ).fetchone()[0]
    finally:
        connection.close()


def sample_resume():
    return next(RESUMES.rglob("candidate_01.txt"))


def test_single_resume_ingestion():
    result = ingest_resume(sample_resume())

    assert result["status"] == "INSERTED"
    assert result["name"] == "Rahul Sharma"
    assert count_records("candidates") == 1
    assert count_records("resumes") == 1


def test_duplicate_prevention():
    first = ingest_resume(sample_resume())
    second = ingest_resume(sample_resume())

    assert first["candidate_id"] == second["candidate_id"]
    assert second["status"] == "UPDATED"
    assert count_records("candidates") == 1
    assert count_records("resumes") == 1


def test_cross_format_ingestion():
    results = []

    for extension in ["pdf", "docx", "txt"]:
        path = next(
            RESUMES.rglob(f"candidate_01.{extension}")
        )
        results.append(ingest_resume(path))

    assert len({
        r["candidate_id"] for r in results
    }) == 1

    assert count_records("candidates") == 1
    assert count_records("resumes") == 1


def test_batch_ingestion():
    results = ingest_folder(RESUMES)

    assert len(results) == 21

    assert sum(
        r["status"] == "INSERTED" for r in results
    ) == 6

    assert sum(
        r["status"] == "UPDATED" for r in results
    ) == 15

    assert any(
        r["name"] == "Aarav Demo"
        for r in results
    )

    assert count_records("candidates") == 6
    assert count_records("resumes") == 6


def test_repeated_batch_ingestion():
    first = ingest_folder(RESUMES)
    second = ingest_folder(RESUMES)

    assert len(first) == len(second) == 21

    assert all(
        r["status"] == "UPDATED" for r in second
    )

    assert {
        r["candidate_id"] for r in first
    } == {
        r["candidate_id"] for r in second
    }

    assert count_records("candidates") == 6
    assert count_records("resumes") == 6


def test_structured_json_storage():
    result = ingest_resume(sample_resume())
    connection = db.get_connection()

    try:
        row = connection.execute(
            """
            SELECT raw_text, parsed_json
            FROM resumes
            WHERE candidate_id = ?
            """,
            (result["candidate_id"],)
        ).fetchone()

        parsed = json.loads(row["parsed_json"])

        assert row["raw_text"].strip()
        assert parsed["name"] == "Rahul Sharma"
        assert "Python" in parsed["skills"]
        assert parsed["years_exp"] == 3
        assert "nlp_entities" in parsed

    finally:
        connection.close()


def test_empty_resume_rejection(tmp_path):
    path = tmp_path / "empty.txt"
    path.write_text("", encoding="utf-8")

    with pytest.raises(ValueError):
        ingest_resume(path)

    assert count_records("candidates") == 0
    assert count_records("resumes") == 0


def test_missing_file_rejection(tmp_path):
    with pytest.raises(ValueError):
        ingest_resume(tmp_path / "missing.txt")

    assert count_records("candidates") == 0


def test_invalid_folder_rejection(tmp_path):
    with pytest.raises(ValueError):
        ingest_folder(tmp_path / "missing_folder")


def test_database_integrity():
    ingest_folder(RESUMES)
    connection = db.get_connection()

    try:
        assert not connection.execute(
            "PRAGMA foreign_key_check"
        ).fetchall()

        assert connection.execute(
            "PRAGMA integrity_check"
        ).fetchone()[0] == "ok"

    finally:
        connection.close()

def test_missing_email_ingestion(tmp_path):
    path = tmp_path / "no_email.txt"
    path.write_text(
        "Name: Demo Candidate\n"
        "Role: Python Developer\n"
        "Skills: Python, SQL\n",
        encoding="utf-8"
    )

    first = ingest_resume(path)
    second = ingest_resume(path)

    assert first["status"] == "INSERTED"
    assert second["status"] == "UPDATED"
    assert first["email"] is None
    assert first["candidate_id"] == second["candidate_id"]
    assert count_records("candidates") == 1


def test_distinct_profiles_without_email(tmp_path):
    first_path = tmp_path / "first.txt"
    second_path = tmp_path / "second.txt"

    first_path.write_text(
        "Name: Demo Candidate\nSkills: Python",
        encoding="utf-8"
    )

    second_path.write_text(
        "Name: Demo Candidate\nSkills: Java",
        encoding="utf-8"
    )

    first = ingest_resume(first_path)
    second = ingest_resume(second_path)

    assert first["candidate_id"] != second["candidate_id"]
    assert count_records("candidates") == 2

