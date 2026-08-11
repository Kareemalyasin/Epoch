"""Scrapes GitHub's trending page since it has no RSS feed.

Its output is shaped to match fetch.py's entries so run.py can treat all
sources uniformly.
"""

import httpx
from bs4 import BeautifulSoup

from app.models.article import Section

GITHUB_TRENDING_URL = "https://github.com/trending?since=daily"
USER_AGENT = "Mozilla/5.0 (compatible; AINewsAggregatorBot/1.0)"


def fetch_github_trending() -> list[dict]:
    """Fetch and parse today's trending repos from GitHub's trending page.

    Called by fetch_all_new_entries()-equivalent logic in run.py, alongside
    the RSS sources, since GitHub Trending has no feed of its own.
    """
    try:
        response = httpx.get(
            GITHUB_TRENDING_URL,
            timeout=10,
            headers={"User-Agent": USER_AGENT},
        )
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        repo_articles = soup.find_all("article", class_="Box-row")

        entries = []
        for repo_article in repo_articles:
            h2 = repo_article.find("h2")
            if not h2:
                continue

            link_tag = h2.find("a")
            if not link_tag or not link_tag.get("href"):
                continue

            repo_path = link_tag["href"].strip("/")
            repo_url = f"https://github.com/{repo_path}"

            description_tag = repo_article.find("p")
            description = description_tag.get_text(strip=True) if description_tag else ""

            entries.append(
                {
                    "title": repo_path,
                    "link": repo_url,
                    "published_at": None,
                    "source_name": "GitHub Trending",
                    "default_section": Section.open_source,
                    "prefetched_text": description,
                    "rss_description": None,
                }
            )

        return entries
    except Exception as exc:
        print(f"[fetch_github_trending] Failed to fetch GitHub trending page: {exc}")
        return []
