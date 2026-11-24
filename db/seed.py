
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.database import get_connection, initialize_database


def seed_database():
    initialize_database()
    conn = get_connection()

    try:
        conn.executemany(
            """
            INSERT OR IGNORE INTO jobs
            (id, title, jd_text, must_have,
             nice_to_have, min_exp_years, location)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    "JOB001",
                    "Python Developer",
                    "Python developer with SQL and API skills",
                    json.dumps(["Python", "SQL"]),
                    json.dumps(["FastAPI", "Git"]),
                    2,
                    "Hyderabad"
                ),
                (
                    "JOB002",
                    "Data Analyst",
                    "Data analyst with Python and Excel skills",
                    json.dumps(["Python", "Excel"]),
                    json.dumps(["SQL", "Power BI"]),
                    1,
                    "Bengaluru"
                )
            ]
        )

        conn.executemany(
            """
            INSERT OR IGNORE INTO candidates
            (id, name, email, phone, location)
            VALUES (?, ?, ?, ?, ?)
            """,
            [
                ("CAN001", "Demo Candidate A",
                 "candidate.a@example.com", None, "Hyderabad"),
                ("CAN002", "Demo Candidate B",
                 "candidate.b@example.com", None, "Bengaluru"),
                ("CAN003", "Demo Candidate C",
                 "candidate.c@example.com", None, "Chennai")
            ]
        )

        conn.executemany(
            """
            INSERT OR IGNORE INTO resumes
            (candidate_id, source, raw_text, parsed_json)
            VALUES (?, ?, ?, ?)
            """,
            [
                (
                    "CAN001", "synthetic_a.txt",
                    "Python SQL FastAPI Git developer",
                    json.dumps({
                        "skills": ["Python", "SQL", "FastAPI", "Git"],
                        "years_exp": 3
                    })
                ),
                (
                    "CAN002", "synthetic_b.txt",
                    "Python Excel SQL Power BI analyst",
                    json.dumps({
                        "skills": ["Python", "Excel", "SQL", "Power BI"],
                        "years_exp": 2
                    })
                ),
                (
                    "CAN003", "synthetic_c.txt",
                    "Java HTML CSS developer",
                    json.dumps({
                        "skills": ["Java", "HTML", "CSS"],
                        "years_exp": 1
                    })
                )
            ]
        )

        conn.executemany(
            """
            INSERT OR IGNORE INTO features
            (candidate_id, job_id, sim_embedding,
             rule_musthave_hits, rule_musthave_total,
             years_exp, gap_penalty)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            [
                ("CAN001", "JOB001", 0.85, 2, 2, 3, 0),
                ("CAN002", "JOB001", 0.65, 2, 2, 2, 0),
                ("CAN003", "JOB001", 0.20, 0, 2, 1, 0)
            ]
        )

        conn.executemany(
            """
            INSERT OR IGNORE INTO rankings
            (job_id, candidate_id, score, reasons)
            VALUES (?, ?, ?, ?)
            """,
            [
                ("JOB001", "CAN001", 90,
                 json.dumps({"synthetic": True, "matched": ["Python", "SQL"]})),
                ("JOB001", "CAN002", 75,
                 json.dumps({"synthetic": True, "matched": ["Python", "SQL"]})),
                ("JOB001", "CAN003", 25,
                 json.dumps({"synthetic": True, "matched": []}))
            ]
        )

        conn.commit()
        print("SYNTHETIC DATA INSERTED SUCCESSFULLY")

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


if __name__ == "__main__":
    seed_database()
