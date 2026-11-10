import os
import sqlite3
from pathlib import Path
from uuid import uuid4


DB_PATH = Path(
    os.getenv(
        "TICKETS_DB_PATH",
        str(
            Path(__file__).resolve().parents[2]
            / "data"
            / "tickets.db"
        ),
    )
)


def create_ticket(
    user_id: str,
    message: str,
    reason: str,
) -> dict:
    """Persist a simulated human-review ticket."""

    DB_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    ticket_id = f"ESC-{uuid4().hex[:8].upper()}"

    with sqlite3.connect(DB_PATH) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS tickets (
                ticket_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                message TEXT NOT NULL,
                reason TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        connection.execute(
            """
            INSERT INTO tickets (
                ticket_id,
                user_id,
                message,
                reason,
                status
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                ticket_id,
                user_id,
                message,
                reason,
                "pending_human_review",
            ),
        )

    return {
        "ticket_id": ticket_id,
        "status": "pending_human_review",
        "reason": reason,
    }
