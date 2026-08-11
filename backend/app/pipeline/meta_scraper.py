"""Scrapes Meta's AI blog with Playwright since it has no RSS feed and the
page is JavaScript-rendered.

The page has two distinct card layouts: a dated "latest news" grid (title in
an aria-label or plain anchor text, date as plain sibling text) and an
undated carousel section containing duplicate DOM nodes of the same few
articles (a common infinite-scroll pattern). Each article typically has two
duplicate anchors pointing to the same URL — an image-wrapping one (often
carrying just a badge label like "FEATURED", sometimes with no usable title
or date info) and a text one (which usually carries the real title and, in
the "latest news" grid, a sibling date). Extraction is done in two passes:
first grouping all anchors by URL, then picking the best title and best date
across all of a URL's anchors, rather than trusting whichever anchor is
encountered first.

Its output is shaped to match fetch.py's entries so run.py can treat all
sources uniformly.
"""

import logging
import re
from datetime import datetime, timezone

from playwright.sync_api import sync_playwright

from app.models.article import Section
from app.pipeline.fetch import apply_recency_with_fallback

logger = logging.getLogger(__name__)

META_BLOG_URL = "https://ai.meta.com/blog/"
MAX_RESULTS = 20

# Badge-like labels that aren't real article titles (e.g. "FEATURED" badges,
# with or without the decorative characters some fonts render around them).
_BADGE_LABELS = {"featured"}


def _is_badge_like(text: str) -> bool:
    """True if text looks like a badge label rather than a real title."""
    letters_only = re.sub(r"[^a-zA-Z]", "", text).lower()
    if not letters_only:
        return True
    if letters_only in _BADGE_LABELS:
        return True
    if len(letters_only) < 4:
        return True
    return False


def _extract_title(link) -> str | None:
    """Prefer the anchor's aria-label (stripping a leading "Read " prefix);
    fall back to the anchor's own inner_text() if there's no aria-label.
    Returns None (not empty string) if no usable, non-badge-like title
    could be extracted from this specific anchor.
    """
    aria_label = link.get_attribute("aria-label")
    if aria_label:
        title = aria_label.strip()
        if title.startswith("Read "):
            title = title[len("Read "):]
        title = title.strip()
        if title and not _is_badge_like(title):
            return title

    text_title = link.inner_text().strip()
    if text_title and not _is_badge_like(text_title):
        return text_title

    return None


_MAX_ANCESTOR_LEVELS = 3


def _extract_published_at(link):
    """Walk up to _MAX_ANCESTOR_LEVELS ancestor levels above the anchor,
    checking each level's direct children for text that parses as a
    "%b %d, %Y" date (same format as Anthropic). Returns the first match
    found, starting from the closest ancestor and moving outward, or None
    if no level yields a parseable date or the structure doesn't match
    what's expected.
    """
    try:
        current = link
        for _ in range(_MAX_ANCESTOR_LEVELS):
            parent_handle = current.evaluate_handle("el => el.parentElement")
            parent = parent_handle.as_element()
            if parent is None:
                return None

            siblings = parent.query_selector_all(":scope > *")
            for sibling in siblings:
                text = sibling.inner_text().strip()
                if not text:
                    continue
                try:
                    parsed = datetime.strptime(text, "%b %d, %Y")
                    return parsed.replace(tzinfo=timezone.utc)
                except ValueError:
                    continue

            current = parent

        return None
    except Exception:
        return None


def fetch_meta_ai_news() -> list[dict]:
    """Fetch and parse recent news entries from Meta's AI blog.

    Called by run.py alongside the RSS sources, since Meta AI Blog has no
    feed of its own. Article body text is not scraped here — the pipeline
    fetches it separately via fetch_article_text() from fetch.py, same as
    RSS entries.
    """
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            try:
                page = browser.new_page()
                page.goto(META_BLOG_URL, wait_until="networkidle")

                links = page.query_selector_all("a[href*='/blog/']")

                # First pass: group all anchors by the URL they point to,
                # since each article typically has two complementary anchors.
                url_to_links: dict[str, list] = {}
                url_order: list[str] = []
                for link in links:
                    href = link.get_attribute("href")
                    if not href:
                        continue

                    url = f"https://ai.meta.com{href}" if href.startswith("/") else href

                    # Skip the blog index page itself.
                    if url.rstrip("/") == META_BLOG_URL.rstrip("/"):
                        continue

                    if url not in url_to_links:
                        url_to_links[url] = []
                        url_order.append(url)
                    url_to_links[url].append(link)

                # Second pass: for each unique URL, pick the best title and
                # best date across all of its anchors.
                entries = []
                for url in url_order:
                    anchors = url_to_links[url]

                    title = None
                    for anchor in anchors:
                        title = _extract_title(anchor)
                        if title:
                            break

                    if not title:
                        continue

                    published_at = None
                    for anchor in anchors:
                        published_at = _extract_published_at(anchor)
                        if published_at is not None:
                            break

                    entries.append(
                        {
                            "title": title,
                            "link": url,
                            "published_at": published_at,
                            "source_name": "Meta AI Blog",
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
        logger.error("fetch_meta_ai_news: failed to scrape Meta AI blog: %s", exc)
        return []
