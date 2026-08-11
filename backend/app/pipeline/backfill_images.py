"""ONE-OFF maintenance script — NOT part of the regular daily pipeline.

Backfills image_url for articles inserted before the image-extraction
feature existed (their image_url is NULL from the ALTER TABLE default, not
because an extraction attempt failed). Only processes articles currently
missing an image, so it's safe to re-run without re-fetching articles that
already succeeded. Run directly with: python -m app.pipeline.backfill_images
"""

import logging

from app.core.logging import setup_logging
from app.db.articles_repo import get_all_grouped, update_article_image
from app.pipeline.fetch import fetch_article_text

logger = logging.getLogger(__name__)


def backfill_all_images() -> None:
    """Fetch each existing article missing an image_url, re-fetch its page,
    and update image_url if an og:image (or twitter:image) is found.
    """
    setup_logging()

    grouped = get_all_grouped()
    articles = [article for section_articles in grouped.values() for article in section_articles]
    logger.info("Backfilling images for %d existing articles.", len(articles))

    updated = 0
    skipped_already_has_image = 0
    skipped_no_image_found = 0

    for article in articles:
        if article.image_url is not None:
            skipped_already_has_image += 1
            logger.debug("'%s' already has an image, skipping.", article.title)
            continue

        text, image_url = fetch_article_text(article.source_url)

        if image_url is None:
            skipped_no_image_found += 1
            logger.debug("No image found for '%s', skipping.", article.title)
            continue

        try:
            update_article_image(str(article.id), image_url)
        except Exception as exc:
            skipped_no_image_found += 1
            logger.error("Failed to update image for '%s': %s", article.title, exc)
            continue

        updated += 1
        logger.info("Updated '%s' with image: %s", article.title, image_url)

    logger.info(
        "Image backfill complete. Updated: %d, skipped (already had image): %d, "
        "skipped (no image found): %d.",
        updated,
        skipped_already_has_image,
        skipped_no_image_found,
    )


if __name__ == "__main__":
    backfill_all_images()
