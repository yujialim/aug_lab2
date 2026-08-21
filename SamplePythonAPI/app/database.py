"""DuckDB-backed persistence layer for tickets."""

from collections.abc import Iterable
from datetime import UTC, datetime
from pathlib import Path
from threading import Lock

import duckdb

from app.models import Ticket, TicketCreate, TicketFilters, TicketPriority, TicketStatus, TicketUpdate


class TicketNotFoundError(LookupError):
    """Raised when a ticket id does not exist in the store."""

    pass


class TicketRepository:
    """Thread-safe CRUD access to tickets stored in a DuckDB database."""

    def __init__(self, database_path: str | Path = "data/tickets.duckdb") -> None:
        """Open (or create) the database at ``database_path`` and initialize schema."""
        self.database_path = str(database_path)
        path = Path(self.database_path)
        if self.database_path != ":memory:":
            path.parent.mkdir(parents=True, exist_ok=True)
        self._connection = duckdb.connect(self.database_path)
        self._lock = Lock()
        self._initialize()

    def close(self) -> None:
        """Close the underlying database connection."""
        self._connection.close()

    def _initialize(self) -> None:
        """Create the ticket sequence and table if they do not already exist."""
        with self._lock:
            self._connection.execute(
                """
                CREATE SEQUENCE IF NOT EXISTS ticket_id_seq START 1;
                CREATE TABLE IF NOT EXISTS tickets (
                    id INTEGER PRIMARY KEY DEFAULT nextval('ticket_id_seq'),
                    title VARCHAR NOT NULL,
                    description VARCHAR NOT NULL,
                    requester VARCHAR NOT NULL,
                    priority VARCHAR NOT NULL,
                    status VARCHAR NOT NULL,
                    created_at TIMESTAMP NOT NULL,
                    updated_at TIMESTAMP NOT NULL
                );
                """
            )

    def seed_defaults(self) -> None:
        """Insert a few sample tickets when the store is empty."""
        with self._lock:
            count = self._connection.execute("SELECT count(*) FROM tickets").fetchone()[0]
        if count:
            return

        samples = [
            TicketCreate(
                title="Laptop cannot connect to VPN",
                description="Requester is blocked from accessing internal systems while traveling.",
                requester="Avery Stone",
                priority=TicketPriority.high,
            ),
            TicketCreate(
                title="New finance dashboard access",
                description="Grant read-only dashboard access for monthly reporting.",
                requester="Mina Patel",
                priority=TicketPriority.medium,
            ),
            TicketCreate(
                title="Broken conference room display",
                description="Display in room Cedar does not wake when connected over HDMI.",
                requester="Jon Bell",
                priority=TicketPriority.low,
            ),
        ]
        for ticket in samples:
            self.create(ticket)

    def create(self, ticket: TicketCreate) -> Ticket:
        """Insert a new ticket in the ``open`` state and return the stored record."""
        now = self._now()
        with self._lock:
            row = self._connection.execute(
                """
                INSERT INTO tickets (title, description, requester, priority, status, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                RETURNING *
                """,
                [
                    ticket.title,
                    ticket.description,
                    ticket.requester,
                    ticket.priority.value,
                    TicketStatus.open.value,
                    now,
                    now,
                ],
            ).fetchone()
        return self._row_to_ticket(row)

    def list(self, filters: TicketFilters | None = None) -> list[Ticket]:
        """Return tickets matching ``filters``, newest first."""
        filters = filters or TicketFilters()
        where_parts: list[str] = []
        parameters: list[str] = []

        if filters.status:
            where_parts.append("status = ?")
            parameters.append(filters.status.value)
        if filters.priority:
            where_parts.append("priority = ?")
            parameters.append(filters.priority.value)
        if filters.search:
            where_parts.append("(title ILIKE ? OR description ILIKE ? OR requester ILIKE ?)")
            search = f"%{filters.search}%"
            parameters.extend([search, search, search])

        query = "SELECT * FROM tickets"
        if where_parts:
            query += " WHERE " + " AND ".join(where_parts)
        query += " ORDER BY updated_at DESC, id DESC"

        with self._lock:
            rows = self._connection.execute(query, parameters).fetchall()
        return [self._row_to_ticket(row) for row in rows]

    def get(self, ticket_id: int) -> Ticket:
        """Return a single ticket or raise :class:`TicketNotFoundError`."""
        with self._lock:
            row = self._connection.execute("SELECT * FROM tickets WHERE id = ?", [ticket_id]).fetchone()
        if row is None:
            raise TicketNotFoundError(f"Ticket {ticket_id} was not found")
        return self._row_to_ticket(row)

    def update(self, ticket_id: int, update: TicketUpdate) -> Ticket:
        """Apply the set fields of ``update`` to a ticket and return the new record."""
        changes = update.model_dump(exclude_unset=True)
        if not changes:
            return self.get(ticket_id)

        assignments: list[str] = []
        parameters: list[object] = []
        for field, value in changes.items():
            assignments.append(f"{field} = ?")
            parameters.append(value.value if hasattr(value, "value") else value)

        assignments.append("updated_at = ?")
        parameters.append(self._now())
        parameters.append(ticket_id)

        with self._lock:
            row = self._connection.execute(
                f"UPDATE tickets SET {', '.join(assignments)} WHERE id = ? RETURNING *",
                parameters,
            ).fetchone()
        if row is None:
            raise TicketNotFoundError(f"Ticket {ticket_id} was not found")
        return self._row_to_ticket(row)

    def delete(self, ticket_id: int) -> None:
        """Delete a ticket or raise :class:`TicketNotFoundError` if it is missing."""
        with self._lock:
            deleted = self._connection.execute(
                "DELETE FROM tickets WHERE id = ? RETURNING id",
                [ticket_id],
            ).fetchone()
        if deleted is None:
            raise TicketNotFoundError(f"Ticket {ticket_id} was not found")

    @staticmethod
    def _now() -> datetime:
        """Return the current UTC time as a naive datetime for storage."""
        return datetime.now(UTC).replace(tzinfo=None)

    @staticmethod
    def _row_to_ticket(row: Iterable[object]) -> Ticket:
        """Map a database row to a :class:`~app.models.Ticket`."""
        keys = ["id", "title", "description", "requester", "priority", "status", "created_at", "updated_at"]
        return Ticket.model_validate(dict(zip(keys, row, strict=True)))
