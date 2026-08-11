"""RSS sources polled by the pipeline to discover new AI news articles."""

from app.models.article import Section

# GitHub Trending, Anthropic Blog, and Meta AI Blog are handled separately
# (see github_trending.py, anthropic_scraper.py, and meta_scraper.py
# respectively) since none of them have a usable RSS feed.
RSS_SOURCES = [
    {
        "name": "OpenAI Blog",
        "url": "https://openai.com/news/rss.xml",
        "default_section": Section.new_models,
    },
    {
        "name": "Google DeepMind Blog",
        "url": "https://deepmind.google/blog/rss.xml",
        "default_section": Section.new_models,
    },
    {
        "name": "Hugging Face Blog",
        "url": "https://huggingface.co/blog/feed.xml",
        "default_section": Section.open_source,
    },
    {
        "name": "TechCrunch AI",
        "url": "https://techcrunch.com/category/artificial-intelligence/feed/",
        "default_section": Section.ai_tools,
    },
    {
        "name": "VentureBeat AI",
        "url": "https://venturebeat.com/category/ai/feed/",
        "default_section": Section.ai_tools,
    },
]

# Fallback logo domains, keyed by source_name, for use when an article has
# no scraped image_url (e.g. the source page had no og:image, or the fetch
# was blocked). Domains are the source's own site, so their favicon reads as
# a legitimate representation of them.
SOURCE_LOGO_DOMAINS = {
    "OpenAI Blog": "openai.com",
    "Google DeepMind Blog": "deepmind.google",
    "Hugging Face Blog": "huggingface.co",
    "TechCrunch AI": "techcrunch.com",
    "VentureBeat AI": "venturebeat.com",
    "GitHub Trending": "github.com",
    "Anthropic Blog": "anthropic.com",
    "Meta AI Blog": "ai.meta.com",
}


def get_source_logo_url(source_name: str) -> str | None:
    """Return a fallback logo image URL for a source, using Google's public
    favicon service, for use when an article has no scraped image_url.
    Returns None if the source isn't in SOURCE_LOGO_DOMAINS.
    """
    domain = SOURCE_LOGO_DOMAINS.get(source_name)
    if domain is None:
        return None
    return f"https://www.google.com/s2/favicons?domain={domain}&sz=128"
