
import sqlite3
from pathlib import Path

from app.schema import TicketCreate, TicketResponse

BASE_DIR = Path(__file__).resolve().parents[2]
DATABASE_PATH = BASE_DIR / "data" / "support_tickets.db"


def get_connection():
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS tickets (
                ticket_id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_name TEXT NOT NULL,
                customer_email TEXT NOT NULL,
                subject TEXT NOT NULL,
                description TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'open'
            )
            """
        )



def create_ticket(request: TicketCreate) -> TicketResponse:
    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO tickets (
                customer_name,
                customer_email,
                subject,
                description,
                status
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                request.customer_name,
                request.customer_email,
                request.subject,
                request.description,
                "open",
            ),
        )

        ticket_id = cursor.lastrowid

        row = connection.execute(
            "SELECT * FROM tickets WHERE ticket_id = ?",
            (ticket_id,),
        ).fetchone()

    return TicketResponse(**dict(row))


def get_all_tickets() -> list[TicketResponse]:
    with get_connection() as connection:
        rows = connection.execute(
            "SELECT * FROM tickets ORDER BY ticket_id DESC"
        ).fetchall()

    return [TicketResponse(**dict(row)) for row in rows]


def get_ticket_by_id(ticket_id: int) -> TicketResponse | None:
    with get_connection() as connection:
        row = connection.execute(
            "SELECT * FROM tickets WHERE ticket_id = ?",
            (ticket_id,),
        ).fetchone()

    if row is None:
        return None

    return TicketResponse(**dict(row))


def get_ticket_status(ticket_id: str) -> str:
    try:
        normalized_id = ticket_id.strip().upper()

        if normalized_id.startswith("TICKET-"):
            normalized_id = normalized_id.removeprefix("TICKET-")

        numeric_id = int(normalized_id)
    except ValueError:
        return f"Invalid ticket ID: {ticket_id}."

    with get_connection() as connection:
        row = connection.execute(
            "SELECT ticket_id, status FROM tickets WHERE ticket_id = ?",
            (numeric_id,),
        ).fetchone()

    if row is None:
        return f"No ticket found with ID {numeric_id}."

    return f"Ticket {row['ticket_id']}: {row['status']}"


initialize_database()
