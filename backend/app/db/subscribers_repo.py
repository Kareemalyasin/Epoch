"""Query functions for the "subscribers" table, built on the shared Supabase client."""

from postgrest.exceptions import APIError

from app.db.client import supabase
from app.models.subscriber import Subscriber, SubscriberCreate

# Postgres error code for a unique constraint violation.
_UNIQUE_VIOLATION_CODE = "23505"


def create_subscriber(subscriber: SubscriberCreate) -> Subscriber:
    """Insert a new subscriber row and return it parsed back into a Subscriber model.

    Called by the signup endpoint when someone subscribes.
    """
    payload = subscriber.model_dump(mode="json")

    try:
        response = supabase.table("subscribers").insert(payload).execute()
    except APIError as exc:
        if exc.code == _UNIQUE_VIOLATION_CODE:
            raise ValueError("Email already subscribed") from exc
        raise

    if not response.data:
        raise ValueError("Insert into 'subscribers' returned no data.")

    return Subscriber(**response.data[0])


def get_active_subscribers_for_section(section: str) -> list[Subscriber]:
    """Fetch all active subscribers subscribed to a given section.

    Called by the daily digest script to find who should receive news for
    a specific section.
    """
    response = (
        supabase.table("subscribers")
        .select("*")
        .eq("is_active", True)
        .contains("subscribed_sections", [section])
        .execute()
    )

    if not response.data:
        return []

    return [Subscriber(**row) for row in response.data]


def deactivate_subscriber_by_token(token: str) -> bool:
    """Deactivate the subscriber matching the given unsubscribe token.

    Called by the unsubscribe endpoint. Returns True if a matching
    subscriber was found and deactivated, False if the token didn't match
    any row (e.g. invalid or already-used) — this is not treated as an
    error, just reported back to the caller.
    """
    response = (
        supabase.table("subscribers")
        .update({"is_active": False})
        .eq("unsubscribe_token", token)
        .eq("is_active", True)
        .execute()
    )

    return bool(response.data)
