import sqlite3
import json
from datetime import datetime

DB_PATH = "research_history.db"


def init_db():
    """
    Creates the research_history table if it doesn't already exist.
    Safe to call every time the app starts.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS research_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT NOT NULL,
            created_at TEXT NOT NULL,
            final_state_json TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def save_research(question: str, final_state: dict) -> int:
    """
    Saves a completed research run to the database.
    Returns the new row's id.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO research_history (question, created_at, final_state_json)
        VALUES (?, ?, ?)
        """,
        (question, datetime.now().isoformat(timespec="seconds"), json.dumps(final_state)),
    )
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return new_id


def get_all_history() -> list:
    """
    Returns a list of past research runs, most recent first.
    Each item: {"id": int, "question": str, "created_at": str}
    (final_state is NOT included here, to keep the list lightweight.)
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, question, created_at FROM research_history ORDER BY id DESC"
    )
    rows = cursor.fetchall()
    conn.close()

    return [
        {"id": row[0], "question": row[1], "created_at": row[2]}
        for row in rows
    ]


def get_history_by_id(history_id: int) -> dict:
    """
    Returns the full final_state dict for a given history id, or None if not found.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT final_state_json FROM research_history WHERE id = ?",
        (history_id,),
    )
    row = cursor.fetchone()
    conn.close()

    if row is None:
        return None

    return json.loads(row[0])