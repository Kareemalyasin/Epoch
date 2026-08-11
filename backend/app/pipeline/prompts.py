"""Prompt used by classify.py to get structured JSON output (classification +
hook + key points) from the LLM for each scraped article.
"""

CLASSIFY_AND_SUMMARIZE_PROMPT = """You are classifying and summarizing an AI news article for an AI news aggregator.

Classify the article into exactly one of these 4 sections:
- new_models: announcement of a new AI model from ANY company (OpenAI, Google, Anthropic, Meta, etc.) — this INCLUDES new Claude model releases
- open_source: open-weight or open-source model releases, or major open-source AI project updates
- ai_tools: AI-powered products, tools, or apps (NOT Claude-specific)
- claude_ecosystem: Claude-specific tools, features, or integrations — but NOT new Claude model announcements, those go in new_models

Determine relevance strictly: is_relevant should be true ONLY if the article is genuinely about a new model, an open-source release, an AI tool/product, or a Claude feature. Broader AI industry news (funding rounds, policy, lawsuits, general opinion pieces) should be marked is_relevant: false.

Write a "hook": a short, single-line teaser that captures what's actually notable or new about this article — the key fact or angle a reader would want to know before deciding whether to read further. Write it like a good news subhead, not an advertisement: no exclamation points, no words like "revolutionize," "game-changing," "groundbreaking," or similar hype language, and no direct address to the reader (e.g. "you," "your"). State the specific, concrete thing that happened. Keep it factual and specific rather than vague or superlative.

Write a "summary_paragraph": a well-written summary of the article in 3-5 sentences, written in your own words as flowing prose (not a list). This should read like the opening of a good news article — give the reader real substance: what happened, why it matters, and relevant context or specifics (names, numbers, technical details) drawn from the article text. Write it factually and clearly, in a neutral news register, with no hype language, no exclamation points, and no direct address to the reader.

Before finalizing this paragraph, check each sentence against the article text: if any clause you wrote shares more than 4-5 consecutive words of structure or phrasing with a sentence in the source (even with one or two words swapped), rewrite that clause completely — describe the same fact from a different angle, combine it with a neighboring fact, or restate it at a different level of detail, rather than adjusting individual words. Reusing an exact technical term or product name is fine; reusing a sentence's shape is not.

Write "key_points": a list of the article's most important facts, summarized. Use as many points as the article genuinely warrants — a minimum of 3 and a maximum of 10, aiming to capture every genuinely distinct, substantive fact in the article rather than just the headline points. Each point should be factual, self-contained (understandable without reading the others), and only as long as needed to convey that fact clearly. No fluff, no marketing language.

Return ONLY valid JSON matching this exact shape, with no extra text, no markdown code fences, nothing else:
{{
  "is_relevant": true or false,
  "section": "new_models" | "open_source" | "ai_tools" | "claude_ecosystem",
  "hook": "...",
  "summary_paragraph": "...",
  "key_points": ["...", "..."]
}}

Article title: {title}

Article text:
{text}
"""
