"""
Update book summaries using AI-generated content.

This script fetches all books from the database and generates
AI-powered summaries for books with missing or poor-quality summaries.
Uses OpenRouter to access AI models for summary generation.
"""

import asyncio
import sys
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

sys.path.insert(0, str(Path(__file__).parent.parent))

load_dotenv()

from app.core.constants import (  # noqa: E402
    AI_SUMMARY_DISCLAIMER,
    OPENAI_RATE_LIMIT_DELAY_SECONDS,
)
from app.core.database import AsyncSessionLocal  # noqa: E402
from app.models.book import Book  # noqa: E402
from app.services.ai_service import generate_book_summary, is_poor_summary  # noqa: E402


async def update_book_summaries(db: AsyncSession | None = None, test_mode: bool = False) -> None:
    """
    Update book summaries using AI generation.

    Identifies books with missing or poor-quality summaries,
    generates new summaries using AI, and updates the database.
    Provides detailed progress tracking and error reporting.

    Args:
        db: Optional database session for testing
        test_mode: If True, only process the first book (for testing)
    """
    print("=" * 60)
    print("🤖 UPDATING BOOK SUMMARIES WITH AI")
    print("=" * 60)

    use_provided_session = db is not None

    if not use_provided_session:
        db = AsyncSessionLocal()

    try:
        if not use_provided_session:
            await db.__aenter__()

        result = await db.execute(select(Book))
        all_books = list(result.scalars().all())
        total_books = len(all_books)

        print(f"\n📊 Found {total_books} books in database")

        books_needing_update = [book for book in all_books if is_poor_summary(book.summary)]

        if test_mode:
            books_needing_update = books_needing_update[:1]
            print("\n🧪 TEST MODE: Processing only the first book")

        books_to_update_count = len(books_needing_update)

        print(f"🔍 Identified {books_to_update_count} books needing summaries")

        if books_to_update_count == 0:
            print("\n✨ All books already have good summaries!")
            print("=" * 60)
            return

        print("-" * 60)

        updated_count = 0
        skipped_count = total_books - books_to_update_count
        failed_count = 0

        for index, book in enumerate(books_needing_update, 1):
            progress = f"[{index}/{books_to_update_count}]"
            book_title_display = book.title[:50] if len(book.title) > 50 else book.title

            print(f"\n{progress} Generating summary for: {book_title_display}")
            print(f"         Author: {book.author}")

            summary = await generate_book_summary(title=book.title, author=book.author, isbn=book.isbn)

            if summary is None:
                print("         ⚠️  Failed to generate summary")
                failed_count += 1
                await asyncio.sleep(OPENAI_RATE_LIMIT_DELAY_SECONDS)
                continue

            book.summary = summary + AI_SUMMARY_DISCLAIMER
            await db.commit()
            print(f"         ✅ Summary generated and saved ({len(summary)} characters)")
            updated_count += 1

            if index % 10 == 0:
                print(f"\n💾 Checkpoint: {index} books completed\n")
                print("-" * 60)

            await asyncio.sleep(OPENAI_RATE_LIMIT_DELAY_SECONDS)

        await db.commit()

        print("\n" + "=" * 60)
        print("✨ UPDATE COMPLETE!")
        print("=" * 60)
        print(f"📚 Updated:  {updated_count} book(s)")
        print(f"⏭️  Skipped:  {skipped_count} book(s)")
        print(f"⚠️  Failed:   {failed_count} book(s)")
        print(f"📊 Total:    {total_books} book(s) in database")
        print("=" * 60)

    except Exception as e:
        await db.rollback()
        print(f"\n❌ Error during update: {e}")
        raise
    finally:
        if not use_provided_session:
            await db.__aexit__(None, None, None)


if __name__ == "__main__":
    test_mode = "--test" in sys.argv or "-t" in sys.argv
    if test_mode:
        print("🧪 Running in TEST MODE (first book only)\n")
    asyncio.run(update_book_summaries(test_mode=test_mode))
