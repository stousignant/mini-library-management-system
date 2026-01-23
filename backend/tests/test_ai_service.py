"""
Tests for AI service module.

Tests the OpenAI integration for generating book summaries.
Uses mocked API responses to avoid actual API calls during testing.
"""

import os
from unittest.mock import Mock, patch

import pytest

from app.services.ai_service import generate_book_summary, is_poor_summary


def mock_getenv(key, default=None):
    """Mock os.getenv that returns test API key for OPENROUTER_API_KEY."""
    if key == "OPENROUTER_API_KEY":
        return "test-api-key"
    return os.environ.get(key, default)


class TestIsPoorSummary:
    """Test suite for is_poor_summary function."""

    def test_returns_true_for_none_summary(self):
        """Test that None summary is considered poor."""
        assert is_poor_summary(None) is True

    def test_returns_true_for_empty_summary(self):
        """Test that empty string summary is considered poor."""
        assert is_poor_summary("") is True

    def test_returns_true_for_whitespace_only_summary(self):
        """Test that whitespace-only summary is considered poor."""
        assert is_poor_summary("   ") is True

    def test_returns_true_for_published_by_indicator(self):
        """Test that 'Published by' indicator is detected as poor."""
        assert is_poor_summary("Published by Random House") is True

    def test_returns_true_for_unknown_publisher_indicator(self):
        """Test that 'Unknown Publisher' indicator is detected as poor."""
        assert is_poor_summary("Unknown Publisher") is True

    def test_returns_false_for_good_summary(self):
        """Test that a proper summary is not considered poor."""
        summary = "A compelling story about a programmer's journey through software development."
        assert is_poor_summary(summary) is False

    def test_returns_true_for_summary_under_10_words(self):
        """Test that summaries with fewer than 10 words are considered poor."""
        summary = "A book about programming and software development."
        word_count = len(summary.split())
        assert word_count == 7
        assert is_poor_summary(summary) is True

    def test_returns_false_for_summary_with_exactly_10_words(self):
        """Test that summaries with exactly 10 words are not considered poor."""
        summary = "This book provides valuable insights into modern software development practices."
        word_count = len(summary.split())
        assert word_count == 10
        assert is_poor_summary(summary) is False

    def test_returns_false_for_summary_over_10_words(self):
        """Test that summaries with more than 10 words are not considered poor."""
        summary = (
            "This comprehensive guide explores the principles and practices "
            "of modern software development and engineering."
        )
        word_count = len(summary.split())
        assert word_count > 10
        assert is_poor_summary(summary) is False


class TestGenerateBookSummary:
    """Test suite for generate_book_summary function."""

    @pytest.mark.asyncio
    async def test_generates_summary_successfully(self):
        """Test successful summary generation with valid book data."""
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="A compelling tale of software craftsmanship."))]

        mock_client = Mock()
        mock_client.chat.send.return_value = mock_response
        mock_client.__enter__ = Mock(return_value=mock_client)
        mock_client.__exit__ = Mock(return_value=False)

        with (
            patch("app.services.ai_service.OpenRouter", return_value=mock_client),
            patch("os.getenv", side_effect=mock_getenv),
        ):
            result = await generate_book_summary(title="Clean Code", author="Robert C. Martin", isbn="9780132350884")

            assert result == "A compelling tale of software craftsmanship."
            mock_client.chat.send.assert_called_once()

    @pytest.mark.asyncio
    async def test_generates_summary_with_missing_isbn(self):
        """Test summary generation when ISBN is None."""
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="An engaging programming book."))]

        mock_client = Mock()
        mock_client.chat.send.return_value = mock_response
        mock_client.__enter__ = Mock(return_value=mock_client)
        mock_client.__exit__ = Mock(return_value=False)

        with (
            patch("app.services.ai_service.OpenRouter", return_value=mock_client),
            patch("os.getenv", side_effect=mock_getenv),
        ):
            result = await generate_book_summary(title="The Pragmatic Programmer", author="Andy Hunt", isbn=None)

            assert result == "An engaging programming book."

    @pytest.mark.asyncio
    async def test_handles_api_error(self):
        """Test that API errors are handled gracefully."""
        mock_client = Mock()
        mock_client.chat.send.side_effect = Exception("API error")
        mock_client.__enter__ = Mock(return_value=mock_client)
        mock_client.__exit__ = Mock(return_value=False)

        with (
            patch("app.services.ai_service.OpenRouter", return_value=mock_client),
            patch("os.getenv", side_effect=mock_getenv),
        ):
            result = await generate_book_summary(title="Test Book", author="Test Author", isbn="1234567890")

            assert result is None

    @pytest.mark.asyncio
    async def test_uses_correct_model_and_parameters(self):
        """Test that correct OpenRouter model and parameters are used."""
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="Test summary"))]

        mock_client = Mock()
        mock_client.chat.send.return_value = mock_response
        mock_client.__enter__ = Mock(return_value=mock_client)
        mock_client.__exit__ = Mock(return_value=False)

        with (
            patch("app.services.ai_service.OpenRouter", return_value=mock_client),
            patch("os.getenv", side_effect=mock_getenv),
        ):
            await generate_book_summary(title="Test Book", author="Test Author", isbn="1234567890")

            call_kwargs = mock_client.chat.send.call_args[1]
            assert call_kwargs["model"] == "openai/gpt-4o-mini"
            assert call_kwargs["max_tokens"] == 500
            assert call_kwargs["temperature"] == 0.7

    @pytest.mark.asyncio
    async def test_prompt_contains_book_details(self):
        """Test that the prompt includes all book details."""
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="Test summary"))]

        mock_client = Mock()
        mock_client.chat.send.return_value = mock_response
        mock_client.__enter__ = Mock(return_value=mock_client)
        mock_client.__exit__ = Mock(return_value=False)

        with (
            patch("app.services.ai_service.OpenRouter", return_value=mock_client),
            patch("os.getenv", side_effect=mock_getenv),
        ):
            await generate_book_summary(title="Clean Code", author="Robert C. Martin", isbn="9780132350884")

            call_kwargs = mock_client.chat.send.call_args[1]
            messages = call_kwargs["messages"]
            user_message = messages[0]["content"]

            assert "Clean Code" in user_message
            assert "Robert C. Martin" in user_message
            assert "9780132350884" in user_message
