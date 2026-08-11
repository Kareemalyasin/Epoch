"""Subscriber signup and unsubscribe API routes."""

from fastapi import APIRouter, HTTPException

from app.db.subscribers_repo import create_subscriber, deactivate_subscriber_by_token
from app.models.subscriber import SubscriberCreate

router = APIRouter(prefix="/subscribers", tags=["subscribers"])


@router.post("/")
def signup(subscriber_data: SubscriberCreate):
    """Sign up a new subscriber.

    Called by the frontend's subscribe form.
    """
    try:
        return create_subscriber(subscriber_data)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc))


@router.get("/unsubscribe/{token}")
def unsubscribe(token: str):
    """Unsubscribe using the token from an unsubscribe link.

    Called by the frontend's unsubscribe page/link.
    """
    if deactivate_subscriber_by_token(token):
        return {"message": "You have been unsubscribed."}

    raise HTTPException(status_code=404, detail="Invalid or already-used unsubscribe link.")
