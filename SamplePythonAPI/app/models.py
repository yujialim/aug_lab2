"""Pydantic models and enums describing tickets and their query filters."""

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class TicketStatus(StrEnum):
    """Lifecycle state of a ticket."""

    open = "open"
    in_progress = "in_progress"
    resolved = "resolved"
    closed = "closed"


class TicketPriority(StrEnum):
    """Relative urgency of a ticket."""

    low = "low"
    medium = "medium"
    high = "high"
    urgent = "urgent"


class TicketCreate(BaseModel):
    """Fields required to open a new ticket."""

    title: str = Field(min_length=3, max_length=120)
    description: str = Field(min_length=3, max_length=2000)
    requester: str = Field(min_length=2, max_length=80)
    priority: TicketPriority = TicketPriority.medium


class TicketUpdate(BaseModel):
    """Partial ticket fields; only set attributes are applied on update."""

    title: str | None = Field(default=None, min_length=3, max_length=120)
    description: str | None = Field(default=None, min_length=3, max_length=2000)
    requester: str | None = Field(default=None, min_length=2, max_length=80)
    priority: TicketPriority | None = None
    status: TicketStatus | None = None


class Ticket(BaseModel):
    """A persisted ticket returned by the API and repository."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str
    requester: str
    priority: TicketPriority
    status: TicketStatus
    created_at: datetime
    updated_at: datetime


class TicketFilters(BaseModel):
    """Optional criteria used to narrow a ticket listing."""

    status: TicketStatus | None = None
    priority: TicketPriority | None = None
    search: str | None = None
