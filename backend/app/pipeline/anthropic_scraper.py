"""Scrapes Anthropic's news page with Playwright since Anthropic has no RSS
feed and the page is JavaScript-rendered.

Its output is shaped to match fetch.py's entries so run.py can treat all
sources uniformly.
"""

import logging
from datetime import datetime, timezone

from playwright.sync_api import sync_playwright

from app.models.article import Section
from app.pipeline.fetch import apply_recency_with_fallback

logger = logging.getLogger(__name__)

ANTHROPIC_NEWS_URL = "https://www.anthropic.com/news"
MAX_RESULTS = 20


def fetch_anthropic_news() -> list[dict]:
    """Fetch and parse recent news entries from Anthropic's news page.

    Called by run.py alongside the RSS sources, since Anthropic has no feed
    of its own. Article body text is not scraped here — the pipeline fetches
    it separately via fetch_article_text() from fetch.py, same as RSS entries.

    Note: the real HTML structure of anthropic.com/news hasn't been
    inspected directly, so the selectors here are a reasonable, defensive
    guess (any <a> whose href contains "/news/" and isn't the index page
    itself). Expect these may need adjusting once we can inspect real
    page output together.
    """
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            try:
                page = browser.new_page()
                page.goto(ANTHROPIC_NEWS_URL, wait_until="networkidle")

                links = page.query_selector_all("a[href*='/news/']")

                seen_urls = set()
                entries = []
                for link in links:
                    href = link.get_attribute("href")
                    if not href:
                        continue

                    url = f"https://www.anthropic.com{href}" if href.startswith("/") else href

                    # Skip the news index page itself and any non-article anchors.
                    if url.rstrip("/") == ANTHROPIC_NEWS_URL.rstrip("/"):
                        continue

                    if url in seen_urls:
                        continue

                    heading = link.query_selector("h2, h4, span[class*='title' i]")
                    if heading is None:
                        continue

                    title = heading.inner_text().strip()
                    if not title:
                        continue

                    published_at = None
                    time_el = link.query_selector("time")
                    if time_el is not None:
                        datetime_str = time_el.get_attribute("datetime")
                        if datetime_str:
                            try:
                                parsed = datetime.fromisoformat(datetime_str)
                                if parsed.tzinfo is None:
                                    parsed = parsed.replace(tzinfo=timezone.utc)
                                published_at = parsed
                            except ValueError:
                                published_at = None

                        if published_at is None:
                            date_text = time_el.inner_text().strip()
                            if date_text:
                                try:
                                    parsed = datetime.strptime(date_text, "%b %d, %Y")
                                    published_at = parsed.replace(tzinfo=timezone.utc)
                                except ValueError:
                                    published_at = None

                    seen_urls.add(url)
                    entries.append(
                        {
                            "title": title,
                            "link": url,
                            "published_at": published_at,
                            "source_name": "Anthropic Blog",
                            "default_section": Section.new_models,
                            "prefetched_text": None,
                            "rss_description": None,
                        }
                    )

                    if len(entries) >= MAX_RESULTS:
                        break

                return apply_recency_with_fallback(entries)
            finally:
                browser.close()
    except Exception as exc:
        logger.error("fetch_anthropic_news: failed to scrape Anthropic news page: %s", exc)
        return []
