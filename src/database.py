
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_DIR = BASE_DIR / "db"
DB_PATH = DB_DIR / "resume_screening.db"
SCHEMA_PATH = DB_DIR / "schema.sql"


def get_connection():
    """Create a database connection."""
    DB_DIR.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(str(DB_PATH))
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")

    return connection


def initialize_database():
    """Initialize the database using the SQL schema."""
    if not SCHEMA_PATH.exists():
        raise FileNotFoundError(
            f"Schema file not found: {SCHEMA_PATH}"
        )

    connection = get_connection()

    try:
        schema = SCHEMA_PATH.read_text(encoding="utf-8-sig")
        connection.executescript(schema)
        connection.commit()
        print("DATABASE INITIALIZED SUCCESSFULLY")

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


if __name__ == "__main__":
    initialize_database()
