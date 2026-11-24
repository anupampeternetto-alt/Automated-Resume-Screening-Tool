
from math import isfinite

from src.database import get_connection


def save_features(candidate_id, job_id, features):
    """Store verified job-related features in SQLite."""

    similarity = features["sim_embedding"]
    experience = features["years_exp"]

    if similarity is None or experience is None:
        return {
            "status": "REVIEW_REQUIRED",
            "reason": "Missing similarity or experience data"
        }

    if not isfinite(similarity) or not -1 <= similarity <= 1:
        raise ValueError("Invalid semantic similarity.")

    if not isfinite(experience) or experience < 0:
        raise ValueError("Invalid experience value.")

    connection = get_connection()

    try:
        connection.execute("BEGIN IMMEDIATE")

        connection.execute(
            """
            INSERT INTO features (
                candidate_id,
                job_id,
                sim_embedding,
                rule_musthave_hits,
                rule_musthave_total,
                years_exp,
                gap_penalty
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(candidate_id, job_id)
            DO UPDATE SET
                sim_embedding = excluded.sim_embedding,
                rule_musthave_hits = excluded.rule_musthave_hits,
                rule_musthave_total = excluded.rule_musthave_total,
                years_exp = excluded.years_exp,
                gap_penalty = excluded.gap_penalty
            """,
            (
                candidate_id,
                job_id,
                similarity,
                features["rule_musthave_hits"],
                features["rule_musthave_total"],
                experience,
                0.0
            )
        )

        connection.execute(
            """
            DELETE FROM rankings
            WHERE candidate_id = ? AND job_id = ?
            """,
            (candidate_id, job_id)
        )

        connection.commit()

        return {
            "status": "SAVED",
            "candidate_id": candidate_id,
            "job_id": job_id
        }

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


def load_features(candidate_id, job_id):
    """Retrieve stored features."""

    connection = get_connection()

    try:
        row = connection.execute(
            """
            SELECT * FROM features
            WHERE candidate_id = ? AND job_id = ?
            """,
            (candidate_id, job_id)
        ).fetchone()

        return dict(row) if row else None

    finally:
        connection.close()
