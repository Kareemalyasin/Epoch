"""Subscriber-related Pydantic models."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.models.article import Section


class Subscriber(BaseModel):
    """A subscriber as stored in the Supabase "subscribers" table."""

    id: UUID
    email: str
    subscribed_sections: list[Section]
    is_active: bool
    unsubscribe_token: UUID
    created_at: datetime


class SubscriberCreate(BaseModel):
    """Fields required to create a new subscriber when someone signs up."""

    email: str
    subscribed_sections: list[Section]
