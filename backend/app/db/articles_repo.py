"""Query functions for the "articles" table, built on the shared Supabase client."""

from datetime import datetime, timedelta, timezone

from app.db.client import supabase
from app.models.article import Article, ArticleCreate, Section


def article_exists(source_url: str) -> bool:
    """Check whether an article with the given source_url already exists.

    Called by the pipeline before inserting a scraped article, to avoid duplicates.
    """
    response = supabase.table("articles").select("id").eq("source_url", source_url).execute()
    return bool(response.data)


def insert_article(article: ArticleCreate) -> Article:
    """Insert a new article row and return it parsed back into an Article model.

    Called by the pipeline once a new article has been scraped and summarized.
    """
    payload = article.model_dump(mode="json")
    response = supabase.table("articles").insert(payload).execute()

    if not response.data:
        raise ValueError("Insert into 'articles' returned no data.")

    return Article(**response.data[0])


def update_article_hook_and_points(article_id: str, hook: str, key_points: list[str]) -> None:
    """Update an existing article's hook and key_points fields by id.

    Called by the one-off hook-regeneration script, not by the regular pipeline.
    """
    response = supabase.table("articles").update({"hook": hook, "key_points": key_points}).eq("id", article_id).execute()
    if not response.data:
        raise ValueError(f"Update failed for article id {article_id}: no data returned.")


def update_article_image(article_id: str, image_url: str | None) -> None:
    """Update an existing article's image_url field by id.

    Called by the one-off image-backfill script, not by the regular pipeline.
    """
    response = supabase.table("articles").update({"image_url": image_url}).eq("id", article_id).execute()
    if not response.data:
        raise ValueError(f"Update failed for article id {article_id}: no data returned.")


def get_recent_articles_by_section(section: str, hours: int = 24) -> list[Article]:
    """Fetch articles in a given section inserted within the last `hours` hours,
    based on created_at (when our pipeline added them, not when they were
    originally published).

    Called by the daily digest script to gather each day's new articles
    per section.
    """
    cutoff = (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat()

    response = (
        supabase.table("articles")
        .select("*")
        .eq("section", section)
        .gte("created_at", cutoff)
        .order("created_at", desc=True)
        .execute()
    )

    if not response.data:
        return []

    return [Article(**row) for row in response.data]


def get_all_grouped() -> dict[str, list[Article]]:
    """Fetch all articles grouped by section, ordered by section then published_at descending.

    Called by the API to serve the aggregated news feed to clients.
    """
    grouped: dict[str, list[Article]] = {section.value: [] for section in Section}

    response = (
        supabase.table("articles")
        .select("*")
        .order("section")
        .order("published_at", desc=True)
        .execute()
    )

    if not response.data:
        return grouped

    for row in response.data:
        article = Article(**row)
        grouped[article.section.value].append(article)

    return grouped
