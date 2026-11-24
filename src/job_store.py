import json
from hashlib import sha256
from pathlib import Path

from src.database import get_connection
from src.job_description_parser import parse_job_description


def save_job(file_path):
    path = Path(file_path)
    job = parse_job_description(path)
    raw_text = path.read_text(encoding="utf-8-sig")

    title = job["job_title"]
    experience = job["minimum_experience"]

    if not title or not raw_text.strip():
        raise ValueError("Invalid job description.")

    if experience is None or experience < 0:
        raise ValueError("Invalid minimum experience.")

    job_id = "JOB-" + sha256(
        raw_text.encode("utf-8")
    ).hexdigest()[:24]

    connection = get_connection()

    try:
        connection.execute(
            """
            INSERT INTO jobs (
                id, title, jd_text,
                must_have, nice_to_have,
                min_exp_years
            )
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO NOTHING
            """,
            (
                job_id,
                title,
                raw_text,
                json.dumps(job["required_skills"]),
                json.dumps(job["preferred_skills"]),
                experience
            )
        )

        connection.commit()

        return {
            "job_id": job_id,
            "title": title,
            "status": "SAVED"
        }

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()
