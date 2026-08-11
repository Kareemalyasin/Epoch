"""Articles API routes."""

from fastapi import APIRouter

from app.db.articles_repo import get_all_grouped

router = APIRouter(prefix="/articles", tags=["articles"])


@router.get("/grouped")
def get_grouped_articles():
    """Return all articles grouped by section.

    This is the main endpoint the frontend calls to populate all 4 sections
    in a single request.
    """
    return get_all_grouped()
