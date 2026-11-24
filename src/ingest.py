import json
from pathlib import Path
from uuid import uuid4

from src.database import get_connection
from src.resume_parser import extract_resume_text
from src.nlp_extractor import extract_hybrid_information


def ingest_resume(file_path):
    """Extract and store resume information in SQLite."""

    path = Path(file_path)
    raw_text = extract_resume_text(path)

    if not raw_text or not raw_text.strip():
        raise ValueError("No readable resume text found.")

    candidate = extract_hybrid_information(raw_text)

    name = candidate.get("name")
    email = candidate.get("email")

    if not name or name == "Not Found":
        raise ValueError("Candidate name could not be extracted.")

    if not email or email == "Not Found":
        raise ValueError("Candidate email could not be extracted.")

    email = email.strip().lower()

    candidate["email"] = email
    candidate["file_name"] = path.name
    candidate["years_exp"] = candidate.get("experience")

    parsed_json = json.dumps(
        candidate,
        ensure_ascii=False
    )

    connection = get_connection()

    try:
        connection.execute("BEGIN IMMEDIATE")

        existing = connection.execute(
            """
            SELECT id FROM candidates
            WHERE LOWER(TRIM(email)) = ?
            """,
            (email,)
        ).fetchall()

        if len(existing) > 1:
            raise ValueError("Multiple candidates share this email.")

        if existing:
            candidate_id = existing[0]["id"]

            previous = connection.execute(
                """
                SELECT raw_text, parsed_json FROM resumes
                WHERE candidate_id = ?
                """,
                (candidate_id,)
            ).fetchone()

            connection.execute(
                """
                UPDATE candidates
                SET name = ?, email = ?
                WHERE id = ?
                """,
                (name, email, candidate_id)
            )

            if previous and (
                previous["raw_text"] != raw_text
                or previous["parsed_json"] != parsed_json
            ):
                connection.execute(
                    "DELETE FROM rankings WHERE candidate_id = ?",
                    (candidate_id,)
                )

                connection.execute(
                    "DELETE FROM features WHERE candidate_id = ?",
                    (candidate_id,)
                )

            status = "UPDATED"

        else:
            candidate_id = "CAN-" + uuid4().hex

            connection.execute(
                """
                INSERT INTO candidates (id, name, email)
                VALUES (?, ?, ?)
                """,
                (candidate_id, name, email)
            )

            status = "INSERTED"

        connection.execute(
            """
            INSERT INTO resumes (
                candidate_id,
                source,
                raw_text,
                parsed_json
            )
            VALUES (?, ?, ?, ?)
            ON CONFLICT(candidate_id) DO UPDATE SET
                source = excluded.source,
                raw_text = excluded.raw_text,
                parsed_json = excluded.parsed_json,
                updated_at = CURRENT_TIMESTAMP
            """,
            (
                candidate_id,
                path.name,
                raw_text,
                parsed_json
            )
        )

        connection.commit()

        return {
            "candidate_id": candidate_id,
            "name": name,
            "email": email,
            "source": path.name,
            "status": status
        }

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


def ingest_folder(folder_path):
    """Ingest supported resume files from a folder."""

    folder = Path(folder_path)

    if not folder.is_dir():
        raise ValueError("Resume folder does not exist.")

    supported = {".pdf", ".docx", ".txt"}

    results = []

    for path in sorted(folder.rglob("*")):
        if path.is_file() and path.suffix.lower() in supported:
            try:
                results.append(ingest_resume(path))

            except Exception as error:
                results.append({
                    "source": path.name,
                    "status": "FAILED",
                    "error": str(error)
                })

    return results