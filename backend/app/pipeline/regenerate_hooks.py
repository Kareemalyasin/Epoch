"""ONE-OFF maintenance script — NOT part of the regular daily pipeline.

Regenerates hook/key_points for every already-inserted article after the
CLASSIFY_AND_SUMMARIZE_PROMPT wording changed (see prompts.py). Re-fetches
and re-classifies every existing article, which costs OpenAI API calls
proportional to the DB size — do not run this casually or wire it into the
daily cron. Run directly with: python -m app.pipeline.regenerate_hooks
"""

import logging

from app.core.logging import setup_logging
from app.db.articles_repo import get_all_grouped, update_article_hook_and_points
from app.pipeline.classify import classify_and_summarize
from app.pipeline.fetch import fetch_article_text, fetch_feed_entries
from app.pipeline.sources import RSS_SOURCES

logger = logging.getLogger(__name__)


def _build_rss_description_lookup() -> dict[str, str]:
    """Fetch each RSS source once and build a link -> rss_description lookup.

    Article rows pulled from the DB don't carry an rss_description field
    (unlike the ephemeral entry dicts a live pipeline run works with), so
    this rebuilds an equivalent lookup here for the same fallback behavior
    run.py uses when a full-text fetch fails (e.g. a 403).
    """
    lookup: dict[str, str] = {}
    for source in RSS_SOURCES:
        for entry in fetch_feed_entries(source):
            if entry["link"] and entry["rss_description"]:
                lookup[entry["link"]] = entry["rss_description"]
    return lookup


def regenerate_all_hooks() -> None:
    """Re-fetch, re-classify, and update hook/key_points for every existing
    article in the DB using the current CLASSIFY_AND_SUMMARIZE_PROMPT.
    """
    setup_logging()

    grouped = get_all_grouped()
    articles = [article for section_articles in grouped.values() for article in section_articles]
    logger.info("Regenerating hooks for %d existing articles.", len(articles))

    rss_description_lookup = _build_rss_description_lookup()

    updated = 0
    skipped = 0

    for article in articles:
        # image_url is captured from fetch_article_text()'s tuple return but
        # intentionally unused here: this script's job is fixing hooks/
        # key_points, not backfilling images. Backfilling image_url for
        # existing rows is a separate, deliberate task if/when it's needed.
        text, image_url = fetch_article_text(article.source_url)
        if not text:
            fallback_description = rss_description_lookup.get(article.source_url)
            if fallback_description:
                logger.info(
                    "Full text fetch failed for '%s', falling back to RSS description.", article.title
                )
                text = fallback_description

        result = classify_and_summarize(article.title, text)

        if result is None:
            skipped += 1
            logger.warning("Skipping '%s': classification/summarization failed.", article.title)
            continue

        if not result["is_relevant"]:
            skipped += 1
            logger.warning("Skipping '%s': classified as not relevant on re-run.", article.title)
            continue

        try:
            update_article_hook_and_points(str(article.id), result["hook"], result["key_points"])
        except Exception as exc:
            skipped += 1
            logger.error("Failed to update '%s': %s", article.title, exc)
            continue

        updated += 1
        logger.info(
            "Updated '%s'.\n  OLD hook: %s\n  NEW hook: %s",
            article.title,
            article.hook,
            result["hook"],
        )

    logger.info(
        "Hook regeneration complete. Updated: %d, skipped: %d.",
        updated,
        skipped,
    )


if __name__ == "__main__":
    regenerate_all_hooks()
