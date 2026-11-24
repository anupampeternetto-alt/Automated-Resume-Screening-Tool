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

    assert len(results) == 15
    assert sum(
        r["status"] == "INSERTED" for r in results
    ) == 5
    assert sum(
        r["status"] == "UPDATED" for r in results
    ) == 10

    assert count_records("candidates") == 5
    assert count_records("resumes") == 5


def test_repeated_batch_ingestion():
    first = ingest_folder(RESUMES)
    second = ingest_folder(RESUMES)

    assert len(first) == len(second) == 15
    assert all(
        r["status"] == "UPDATED" for r in second
    )

    assert count_records("candidates") == 5
    assert count_records("resumes") == 5


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