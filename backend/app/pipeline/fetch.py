"""Fetches RSS feed entries and article text for the pipeline."""

from calendar import timegm
from datetime import datetime, timedelta, timezone

import feedparser
import httpx
from bs4 import BeautifulSoup

from app.pipeline.sources import RSS_SOURCES

USER_AGENT = "Mozilla/5.0 (compatible; AINewsAggregatorBot/1.0)"

# Some feeds (e.g. OpenAI's) return their entire multi-year archive on every
# request. Only keep entries published within this window so a single run
# doesn't churn through thousands of old posts. Entries with no published
# date can't be verified as recent, so they're dropped rather than assumed.
RECENCY_WINDOW_DAYS = 7

# Cap on how old a fallback entry is allowed to be. Fallback exists so a
# quiet source still contributes something rather than going empty, but a
# "most recent" item from months ago is stale enough to be misleading as
# news rather than merely a bit behind — so fallback has its own outer limit.
FALLBACK_MAX_AGE_DAYS = 30


def apply_recency_with_fallback(entries: list[dict], fallback_count: int = 3) -> list[dict]:
    """Filter entries to those published within RECENCY_WINDOW_DAYS days.

    If nothing falls within that window (e.g. a source that's gone quiet),
    fall back to the fallback_count most recent entries published within
    FALLBACK_MAX_AGE_DAYS days instead of returning an empty list — so a
    source with nothing published very recently still contributes its most
    recent items rather than going completely empty. If nothing is within
    FALLBACK_MAX_AGE_DAYS days either, return an empty list rather than
    surfacing very stale content as if it were current. Entries with no
    published_at are excluded from the fallback tier too, since we can't
    verify they're within FALLBACK_MAX_AGE_DAYS days.

    Used by all sources (RSS, Anthropic, Meta) for consistent behavior.
    Not used by GitHub Trending, whose entries always have published_at
    of None — applying this there would always hit the fallback branch
    and needlessly shrink its results to fallback_count every run.
    """
    now = datetime.now(timezone.utc)
    recency_cutoff = now - timedelta(days=RECENCY_WINDOW_DAYS)

    within_window = [
        entry for entry in entries if entry["published_at"] is not None and entry["published_at"] >= recency_cutoff
    ]
    if within_window:
        return within_window

    fallback_cutoff = now - timedelta(days=FALLBACK_MAX_AGE_DAYS)
    within_fallback_window = [
        entry for entry in entries if entry["published_at"] is not None and entry["published_at"] >= fallback_cutoff
    ]
    if not within_fallback_window:
        return []

    return sorted(within_fallback_window, key=lambda entry: entry["published_at"], reverse=True)[:fallback_count]


def fetch_feed_entries(source: dict) -> list[dict]:
    """Fetch and normalize entries from a single RSS source dict, then apply
    apply_recency_with_fallback() so a quiet feed still contributes its most
    recent items instead of returning nothing.

    Called by fetch_all_new_entries() during a pipeline run.
    """
    try:
        feed = feedparser.parse(source["url"])
    except Exception as exc:
        print(f"[fetch_feed_entries] Failed to fetch '{source['name']}' ({source['url']}): {exc}")
        return []

    entries = []
    for entry in feed.entries:
        published_at = None
        if getattr(entry, "published_parsed", None):
            published_at = datetime.fromtimestamp(timegm(entry.published_parsed), tz=timezone.utc)

        entries.append(
            {
                "title": entry.get("title", ""),
                "link": entry.get("link", ""),
                "published_at": published_at,
                "source_name": source["name"],
                "default_section": source["default_section"],
                "prefetched_text": None,
                "rss_description": entry.get("summary", "") or entry.get("description", ""),
            }
        )

    return apply_recency_with_fallback(entries)


def extract_og_image(soup: BeautifulSoup) -> str | None:
    """Extract the article's preview image URL from its page metadata.

    Tries the Open Graph og:image tag first, falling back to Twitter's
    twitter:image tag (many sites set one or the other, or both). Returns
    None if neither is present or on any failure.
    """
    try:
        og_tag = soup.find("meta", property="og:image")
        if og_tag and og_tag.get("content"):
            return og_tag["content"]

        twitter_tag = soup.find("meta", attrs={"name": "twitter:image"})
        if twitter_tag and twitter_tag.get("content"):
            return twitter_tag["content"]

        return None
    except Exception:
        return None


def fetch_article_text(url: str) -> tuple[str, str | None]:
    """Fetch an article page and extract its visible <p> text (truncated to
    6000 characters) along with its preview image URL, if any.

    Called by the pipeline when summarizing an article before insertion.
    Returns (text, image_url); either may be empty/None on failure.
    """
    try:
        response = httpx.get(
            url,
            timeout=10,
            headers={"User-Agent": USER_AGENT},
            follow_redirects=True,
        )
        response.raise_for_status()
    except Exception as exc:
        print(f"[fetch_article_text] Failed to fetch '{url}': {exc}")
        return "", None

    try:
        soup = BeautifulSoup(response.text, "html.parser")
        paragraphs = soup.find_all("p")
        text = "\n".join(p.get_text(strip=True) for p in paragraphs)
        image_url = extract_og_image(soup)
        return text[:6000], image_url
    except Exception as exc:
        print(f"[fetch_article_text] Failed to parse '{url}': {exc}")
        return "", None


def fetch_all_new_entries() -> list[dict]:
    """Fetch entries from every RSS source and combine them into a single flat list.

    Called by run.py at the start of a pipeline run; deduplication against the DB
    happens later in run.py, not here.
    """
    all_entries = []
    for source in RSS_SOURCES:
        entries = fetch_feed_entries(source)
        if not entries:
            print(
                f"[fetch_all_new_entries] No entries fetched from RSS source "
                f"'{source['name']}' (feed may be empty, stale, or temporarily down)."
            )
        all_entries.extend(entries)

    return all_entries
