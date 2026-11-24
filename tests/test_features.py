
import sqlite3

import pytest

import src.database as db
from src.features import (
    calculate_semantic_similarity,
    extract_features
)
from src.feature_store import (
    save_features,
    load_features
)


@pytest.fixture
def test_database(tmp_path, monkeypatch):

    monkeypatch.setattr(
        db, "DB_PATH", tmp_path / "test.db"
    )

    db.initialize_database()

    connection = db.get_connection()

    connection.execute(
        """
        INSERT INTO candidates (id, name, email)
        VALUES ('C1', 'Sample Candidate', 'test@example.com')
        """
    )

    connection.execute(
        """
        INSERT INTO jobs (id, title, jd_text)
        VALUES ('J1', 'Python Developer', 'Python and SQL')
        """
    )

    connection.commit()
    connection.close()


@pytest.fixture
def sample_features():

    return {
        "sim_embedding": 0.85,
        "rule_musthave_hits": 2,
        "rule_musthave_total": 3,
        "years_exp": 3.0,
        "gap_penalty": 0.0
    }


def test_semantic_similarity():

    relevant = calculate_semantic_similarity(
        "Python SQL programming",
        "Python software development with SQL"
    )

    unrelated = calculate_semantic_similarity(
        "Python SQL programming",
        "Cooking Italian food"
    )

    assert relevant > unrelated
    assert -1 <= relevant <= 1


def test_identical_text_similarity():

    result = calculate_semantic_similarity(
        "Python SQL", "Python SQL"
    )

    assert result == pytest.approx(1.0, abs=0.001)


def test_empty_similarity_input():

    with pytest.raises(ValueError):
        calculate_semantic_similarity("", "Python")


def test_feature_extraction():

    candidate = {
        "skills": ["Python", "SQL", "Git"],
        "experience": 3.0
    }

    job = {
        "required_skills": ["Python", "SQL"],
        "preferred_skills": ["Git", "Docker"],
        "minimum_experience": 2.0
    }

    result = extract_features(candidate, job)

    assert result["rule_musthave_hits"] == 2
    assert result["rule_musthave_total"] == 2
    assert result["years_exp"] == 3.0
    assert result["review_required"] is True


def test_feature_persistence(
    test_database, sample_features
):

    result = save_features(
        "C1", "J1", sample_features
    )

    assert result["status"] == "SAVED"

    stored = load_features("C1", "J1")

    assert stored["sim_embedding"] == 0.85
    assert stored["years_exp"] == 3.0


def test_feature_update(
    test_database, sample_features
):

    save_features("C1", "J1", sample_features)

    sample_features["sim_embedding"] = 0.95

    save_features("C1", "J1", sample_features)

    stored = load_features("C1", "J1")

    assert stored["sim_embedding"] == 0.95

    connection = db.get_connection()

    count = connection.execute(
        "SELECT COUNT(*) FROM features"
    ).fetchone()[0]

    connection.close()

    assert count == 1


def test_missing_feature_data(
    test_database, sample_features
):

    sample_features["sim_embedding"] = None

    result = save_features(
        "C1", "J1", sample_features
    )

    assert result["status"] == "REVIEW_REQUIRED"
    assert load_features("C1", "J1") is None


def test_invalid_similarity(
    test_database, sample_features
):

    sample_features["sim_embedding"] = 1.5

    with pytest.raises(ValueError):
        save_features("C1", "J1", sample_features)


def test_foreign_key_enforcement(
    test_database, sample_features
):

    with pytest.raises(sqlite3.IntegrityError):
        save_features(
            "INVALID", "J1", sample_features
        )


def test_feature_database_integrity(
    test_database, sample_features
):

    save_features("C1", "J1", sample_features)

    connection = db.get_connection()

    integrity = connection.execute(
        "PRAGMA integrity_check"
    ).fetchone()[0]

    foreign_keys = connection.execute(
        "PRAGMA foreign_key_check"
    ).fetchall()

    connection.close()

    assert integrity == "ok"
    assert foreign_keys == []
