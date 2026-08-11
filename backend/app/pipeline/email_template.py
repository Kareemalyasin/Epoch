"""Builds the HTML for the daily digest email.

The unsubscribe link contains a literal "{token}" placeholder, since this
HTML is built once and reused for every subscriber — the caller must
replace "{token}" with that subscriber's actual unsubscribe_token before
sending.
"""

FRONTEND_URL = "http://localhost:5174"

_CONTAINER_STYLE = (
    "max-width:600px;margin:0 auto;padding:24px;"
    "font-family:Arial,Helvetica,sans-serif;color:#111827;"
)
_HEADER_STYLE = "font-size:24px;font-weight:bold;color:#1a2f56;margin:0 0 24px;"
_SECTION_HEADING_STYLE = (
    "font-size:20px;font-weight:bold;color:#1a2f56;"
    "border-bottom:1px solid #e5e7eb;padding-bottom:8px;margin:32px 0 16px;"
)
_ARTICLE_TITLE_STYLE = "font-size:16px;font-weight:bold;color:#1a2f56;text-decoration:none;"
_ARTICLE_HOOK_STYLE = "font-size:16px;color:#6b7280;margin:6px 0;"
_READ_MORE_STYLE = "font-size:14px;color:#1a2f56;text-decoration:none;"
_FOOTER_STYLE = "font-size:12px;color:#6b7280;margin-top:40px;text-align:center;"
_FOOTER_LINK_STYLE = "color:#6b7280;"


def build_digest_html(sections_with_articles: dict[str, list]) -> str:
    """Build the full digest email HTML from a dict of section label ->
    list of Article objects. Sections with no articles are skipped entirely.
    """
    parts = [
        f'<div style="{_CONTAINER_STYLE}">',
        f'<div style="{_HEADER_STYLE}">Your daily AI news digest</div>',
    ]

    for label, articles in sections_with_articles.items():
        if not articles:
            continue

        parts.append(f'<div style="{_SECTION_HEADING_STYLE}">{label}</div>')

        for article in articles:
            article_url = f"{FRONTEND_URL}/article/{article.id}"
            parts.append(
                '<div style="margin-bottom:20px;">'
                f'<a href="{article_url}" style="{_ARTICLE_TITLE_STYLE}">{article.title}</a>'
                f'<p style="{_ARTICLE_HOOK_STYLE}">{article.hook}</p>'
                f'<a href="{article_url}" style="{_READ_MORE_STYLE}">Read more &rarr;</a>'
                "</div>"
            )

    parts.append(
        f'<div style="{_FOOTER_STYLE}">'
        f'Don\'t want these emails? '
        f'<a href="{FRONTEND_URL}/unsubscribe/{{token}}" style="{_FOOTER_LINK_STYLE}">Unsubscribe here</a>'
        "</div>"
    )

    parts.append("</div>")

    return "".join(parts)
