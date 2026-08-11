"""Classifies and summarizes scraped articles via the OpenAI API."""

import json
import logging

from openai import OpenAI

from app.config import settings
from app.pipeline.prompts import CLASSIFY_AND_SUMMARIZE_PROMPT

logger = logging.getLogger(__name__)

client = OpenAI(api_key=settings.openai_api_key)

REQUIRED_KEYS = {"is_relevant", "section", "hook", "summary_paragraph", "key_points"}

# Prompt instructions alone proved unreliable at preventing summary_paragraph
# from closely mirroring the source article's sentence structure (verified
# empirically: worked on some articles, failed on others). This mechanical
# check catches what the prompt can't guarantee.
MAX_PARAGRAPH_SIMILARITY = 0.15

_SIMILARITY_RETRY_MESSAGE = (
    "Your summary_paragraph was too textually similar to the source article. "
    "Rewrite ONLY the summary_paragraph field completely differently — different "
    "sentence structures, different word choices throughout, while keeping the "
    "same facts. Return the full JSON again with the corrected summary_paragraph."
)


def check_paragraph_similarity(paragraph: str, source_text: str) -> float:
    """Measure how textually similar paragraph is to source_text using 6-word
    sequence (6-gram) overlap.

    Returns the fraction of the paragraph's 6-grams that also appear
    verbatim in the source text's 6-grams (0.0 = no overlap, 1.0 = fully
    copied).
    """

    def get_ngrams(text: str, n: int = 6) -> set[str]:
        words = text.lower().split()
        return {" ".join(words[i : i + n]) for i in range(len(words) - n + 1)}

    paragraph_ngrams = get_ngrams(paragraph)
    if not paragraph_ngrams:
        return 0.0

    source_ngrams = get_ngrams(source_text)
    overlap = paragraph_ngrams & source_ngrams
    return len(overlap) / len(paragraph_ngrams)


def _parse_and_validate(content: str, title: str) -> dict | None:
    """Parse a raw LLM response and confirm it has all required keys."""
    parsed = json.loads(content)

    missing_keys = REQUIRED_KEYS - parsed.keys()
    if missing_keys:
        logger.error(
            "classify_and_summarize: response missing keys %s for article '%s'",
            missing_keys,
            title,
        )
        return None

    return parsed


def classify_and_summarize(title: str, text: str) -> dict | None:
    """Classify and summarize a single scraped article via the LLM.

    Called once per scraped article by run.py. A None return means the
    article failed classification and should be skipped (not inserted
    into the DB) — this function never raises.

    If summary_paragraph comes back too textually similar to the source
    (per check_paragraph_similarity), one retry is attempted asking the
    model to rewrite just that field. If the retry also fails the check
    (or errors), summary_paragraph is set to "" rather than risk publishing
    text too close to the source.
    """
    try:
        prompt = CLASSIFY_AND_SUMMARIZE_PROMPT.format(title=title, text=text)
        messages = [{"role": "user", "content": prompt}]

        response = client.chat.completions.create(
            model=settings.openai_model,
            messages=messages,
            temperature=0.3,
        )

        content = response.choices[0].message.content
        parsed = _parse_and_validate(content, title)
        if parsed is None:
            return None

        similarity = check_paragraph_similarity(parsed["summary_paragraph"], text)
        if similarity > MAX_PARAGRAPH_SIMILARITY:
            logger.info(
                "classify_and_summarize: summary_paragraph for '%s' too similar to source "
                "(%.2f), retrying once.",
                title,
                similarity,
            )

            messages.append({"role": "assistant", "content": content})
            messages.append({"role": "user", "content": _SIMILARITY_RETRY_MESSAGE})

            try:
                retry_response = client.chat.completions.create(
                    model=settings.openai_model,
                    messages=messages,
                    temperature=0.3,
                )
                retry_content = retry_response.choices[0].message.content
                retry_parsed = _parse_and_validate(retry_content, title)

                if retry_parsed is not None:
                    retry_similarity = check_paragraph_similarity(
                        retry_parsed["summary_paragraph"], text
                    )
                    if retry_similarity <= MAX_PARAGRAPH_SIMILARITY:
                        logger.info(
                            "classify_and_summarize: retry succeeded for '%s' (%.2f).",
                            title,
                            retry_similarity,
                        )
                        parsed = retry_parsed
                    else:
                        logger.warning(
                            "classify_and_summarize: retry for '%s' still too similar "
                            "(%.2f); dropping summary_paragraph.",
                            title,
                            retry_similarity,
                        )
                        parsed["summary_paragraph"] = ""
                else:
                    logger.warning(
                        "classify_and_summarize: retry for '%s' returned invalid response; "
                        "dropping summary_paragraph.",
                        title,
                    )
                    parsed["summary_paragraph"] = ""
            except Exception as exc:
                logger.warning(
                    "classify_and_summarize: retry for '%s' failed (%s); dropping summary_paragraph.",
                    title,
                    exc,
                )
                parsed["summary_paragraph"] = ""

        return parsed
    except Exception as exc:
        logger.error(
            "classify_and_summarize: failed to classify/summarize article '%s': %s",
            title,
            exc,
        )
        return None
