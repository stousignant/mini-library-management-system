"""
AI service for generating book summaries using OpenRouter.

Provides functionality to generate engaging book summaries
and detect poor-quality summaries that need regeneration.
Uses OpenRouter to access multiple AI providers through a unified API.
"""

import asyncio
import os

from openrouter import OpenRouter

from app.core.constants import (
    AI_SUMMARY_PROMPT_TEMPLATE,
    MINIMUM_SUMMARY_WORD_COUNT,
    OPENAI_MAX_TOKENS,
    OPENAI_MODEL,
    OPENAI_REQUEST_TIMEOUT_SECONDS,
    OPENAI_TEMPERATURE,
    POOR_SUMMARY_INDICATORS,
)


def is_poor_summary(summary: str | None) -> bool:
    """
    Check if a summary is missing or of poor quality.

    A summary is considered poor if:
    - It is None or empty/whitespace
    - It contains poor quality indicators (e.g., "Published by")
    - It has fewer than the minimum required words

    Args:
        summary: The summary text to check

    Returns:
        True if summary is poor quality or missing, False otherwise
    """
    if summary is None or not summary.strip():
        return True

    for indicator in POOR_SUMMARY_INDICATORS:
        if indicator in summary:
            return True

    word_count = len(summary.split())
    if word_count < MINIMUM_SUMMARY_WORD_COUNT:
        return True

    return False


async def generate_book_summary(title: str, author: str, isbn: str | None) -> str | None:
    """
    Generate an AI-powered book summary using OpenRouter.

    Args:
        title: Book title
        author: Book author
        isbn: Book ISBN (optional)

    Returns:
        Generated summary text or None if generation failed
    """
    try:
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            print("⚠️  Warning: OPENROUTER_API_KEY not set")
            return None

        prompt = AI_SUMMARY_PROMPT_TEMPLATE.format(title=title, author=author, isbn=isbn or "Not available")

        def _sync_call():
            with OpenRouter(api_key=api_key) as client:
                response = client.chat.send(
                    model=OPENAI_MODEL,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=OPENAI_MAX_TOKENS,
                    temperature=OPENAI_TEMPERATURE,
                )

                if not response:
                    raise ValueError(f"Empty response from OpenRouter API. Raw response: {response}")

                if not hasattr(response, "choices") or not response.choices:
                    raise ValueError(f"Response missing 'choices' field or choices is empty. Raw response: {response}")

                first_choice = response.choices[0]
                if not hasattr(first_choice, "message"):
                    raise ValueError(f"First choice missing 'message' field. Raw response: {response}")

                message = first_choice.message
                if not hasattr(message, "content"):
                    raise ValueError(f"Message missing 'content' field. Raw response: {response}")

                content = message.content
                if content is None or (isinstance(content, str) and not content.strip()):
                    raise ValueError(f"Message content is None or empty. Raw response: {response}")

                return content

        summary = await asyncio.wait_for(
            asyncio.to_thread(_sync_call),
            timeout=OPENAI_REQUEST_TIMEOUT_SECONDS,
        )
        return summary

    except asyncio.TimeoutError:
        print(f"⚠️  Timeout: OpenRouter request exceeded {OPENAI_REQUEST_TIMEOUT_SECONDS}s")
        return None
    except Exception as e:
        print(f"⚠️  API error: {e}")
        return None
