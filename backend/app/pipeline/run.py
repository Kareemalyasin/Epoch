"""Main daily pipeline entrypoint.

Ties together fetching (RSS + GitHub Trending + the Anthropic scraper),
classification/summarization via the LLM, and DB insertion. Run once daily
(manually for now, via a scheduler later) with: python -m app.pipeline.run
"""

import logging

from app.core.logging import setup_logging
from app.db.articles_repo import article_exists, insert_article
from app.models.article import ArticleCreate
from app.pipeline.anthropic_scraper import fetch_anthropic_news
from app.pipeline.classify import classify_and_summarize
from app.pipeline.fetch import fetch_all_new_entries, fetch_article_text
from app.pipeline.github_trending import fetch_github_trending
from app.pipeline.meta_scraper import fetch_meta_ai_news

logger = logging.getLogger(__name__)


def run_pipeline() -> None:
    """Run a single pass of the pipeline: fetch all sources, skip duplicates,
    classify/summarize the rest, and insert the relevant ones into the DB.
    """
    setup_logging()
    logger.info("Pipeline run started.")

    entries = fetch_all_new_entries() + fetch_github_trending() + fetch_anthropic_news() + fetch_meta_ai_news()
    logger.info("Fetched %d total entries from all sources.", len(entries))

    inserted = 0
    skipped_duplicate = 0
    skipped_irrelevant = 0
    skipped_failed = 0

    for entry in entries:
        if not entry.get("link"):
            skipped_failed += 1
            logger.warning("Skipping entry with missing link: '%s'", entry.get("title", "<no title>"))
            continue

        if article_exists(entry["link"]):
            skipped_duplicate += 1
            logger.debug("Skipping duplicate: '%s'", entry["title"])
            continue

        text = entry["prefetched_text"]
        image_url = None
        if text is None:
            text, image_url = fetch_article_text(entry["link"])
            if not text and entry.get("rss_description"):
                logger.info("Full text fetch failed for '%s', falling back to RSS description.", entry["title"])
                text = entry["rss_description"]

        result = classify_and_summarize(entry["title"], text)
        if result is None:
            skipped_failed += 1
            logger.warning("Skipping '%s': classification/summarization failed.", entry["title"])
            continue

        if not result["is_relevant"]:
            skipped_irrelevant += 1
            logger.debug("Skipping '%s': classified as not relevant.", entry["title"])
            continue

        try:
            article = ArticleCreate(
                title=entry["title"],
                source_url=entry["link"],
                source_name=entry["source_name"],
                section=result["section"],
                hook=result["hook"],
                summary_paragraph=result["summary_paragraph"],
                key_points=result["key_points"],
                image_url=image_url,
                published_at=entry["published_at"],
            )
            insert_article(article)
        except Exception as exc:
            skipped_failed += 1
            logger.error("Failed to insert '%s': %s", entry["title"], exc)
            continue

        inserted += 1
        logger.info("Inserted '%s' into section '%s'.", entry["title"], result["section"])

    logger.info(
        "Pipeline run complete. Fetched: %d, inserted: %d, skipped (duplicate): %d, "
        "skipped (irrelevant): %d, skipped (failed): %d.",
        len(entries),
        inserted,
        skipped_duplicate,
        skipped_irrelevant,
        skipped_failed,
    )


if __name__ == "__main__":
    run_pipeline()
