"""Daily digest entrypoint. Meant to run once per day (e.g. via a scheduler,
after the news pipeline has finished) with: python -m app.pipeline.send_daily_digest

Each subscriber gets exactly one combined email covering only their chosen
sections' new articles from the last 24 hours — never an empty digest, and
never more than one email even if they're subscribed to multiple sections
that both have news.
"""

import logging

from app.core.logging import setup_logging
from app.db.articles_repo import get_recent_articles_by_section
from app.db.subscribers_repo import get_active_subscribers_for_section
from app.models.article import Section
from app.pipeline.email_sender import send_digest_email
from app.pipeline.email_template import build_digest_html

logger = logging.getLogger(__name__)

SECTION_LABELS = {
    "new_models": "New Models",
    "open_source": "Open Source",
    "ai_tools": "AI Tools",
    "claude_ecosystem": "Claude",
}


def send_all_digests() -> None:
    """Gather today's new articles per section, find subscribers who care
    about them, and send each subscriber one combined digest email.
    """
    setup_logging()
    logger.info("Daily digest run started.")

    articles_by_section = {
        section.value: get_recent_articles_by_section(section.value) for section in Section
    }

    total_articles = sum(len(articles) for articles in articles_by_section.values())
    logger.info("Found %d total new articles across all sections.", total_articles)

    if total_articles == 0:
        logger.info("No new articles today, skipping all sends.")
        return

    subscribers_by_email = {}
    for section_value, articles in articles_by_section.items():
        if not articles:
            continue

        for subscriber in get_active_subscribers_for_section(section_value):
            subscribers_by_email[subscriber.email] = subscriber

    sent = 0
    skipped_no_relevant_news = 0
    failed = 0

    for subscriber in subscribers_by_email.values():
        sections_with_articles = {}
        for section_value in subscriber.subscribed_sections:
            section_key = section_value.value if hasattr(section_value, "value") else section_value
            articles = articles_by_section.get(section_key, [])
            if articles:
                sections_with_articles[SECTION_LABELS[section_key]] = articles

        if not sections_with_articles:
            skipped_no_relevant_news += 1
            logger.debug(
                "Skipping '%s': no new articles in any of their subscribed sections.",
                subscriber.email,
            )
            continue

        html = build_digest_html(sections_with_articles)
        html = html.replace("{token}", str(subscriber.unsubscribe_token))

        if send_digest_email(subscriber.email, "Your daily AI news digest", html):
            sent += 1
        else:
            failed += 1

    logger.info(
        "Daily digest run complete. Sent: %d, skipped (no relevant news): %d, failed: %d.",
        sent,
        skipped_no_relevant_news,
        failed,
    )


if __name__ == "__main__":
    send_all_digests()
