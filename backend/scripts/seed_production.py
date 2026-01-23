"""
Production database seeding script.

Seeds the database with 100 curated books from Open Library API.
Includes progress tracking, error handling, and safety checks.
"""

import asyncio
import sys
from pathlib import Path

import httpx
from sqlalchemy import func, select

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.constants import (
    OPEN_LIBRARY_API_BASE_URL,
    OPEN_LIBRARY_RATE_LIMIT_DELAY_SECONDS,
    OPEN_LIBRARY_REQUEST_TIMEOUT_SECONDS,
    SEED_BOOK_ISBNS,
)
from app.core.database import AsyncSessionLocal
from app.models.book import Book
from app.models.enums import BookStatus


async def fetch_book_metadata(isbn: str) -> dict | None:
    """
    Fetch book metadata from Open Library API.

    Args:
        isbn: ISBN-13 of the book to fetch

    Returns:
        Dictionary with book metadata or None if fetch failed
    """
    url = f"{OPEN_LIBRARY_API_BASE_URL}/api/books?bibkeys=ISBN:{isbn}&format=json&jscmd=data"

    try:
        async with httpx.AsyncClient(timeout=OPEN_LIBRARY_REQUEST_TIMEOUT_SECONDS) as client:
            response = await client.get(url)
            response.raise_for_status()

            data = response.json()
            key = f"ISBN:{isbn}"

            if key not in data:
                return None

            book_data = data[key]
            authors = book_data.get("authors", [])
            author_name = authors[0]["name"] if authors else "Unknown Author"

            publishers = book_data.get("publishers", [])
            publisher_name = publishers[0]["name"] if publishers else "Unknown Publisher"

            cover = book_data.get("cover", {})
            cover_url = cover.get("large") or cover.get("medium") or cover.get("small") or None

            return {
                "title": book_data.get("title", "Unknown Title"),
                "author": author_name,
                "isbn": isbn,
                "cover_image": cover_url,
                "summary": f"Published by {publisher_name}",
                "status": BookStatus.AVAILABLE,
            }

    except httpx.HTTPError:
        return None
    except Exception:
        return None


async def seed_production() -> None:
    """
    Seed production database with curated books from Open Library.

    Features:
    - Progress tracking with counters
    - Duplicate detection by ISBN
    - Error handling and reporting
    - Summary statistics
    """
    print("=" * 60)
    print("🌱 PRODUCTION DATABASE SEEDING")
    print("=" * 60)

    async with AsyncSessionLocal() as db:
        try:
            result = await db.execute(select(func.count(Book.id)))
            current_count = result.scalar()

            print(f"\n📊 Current books in database: {current_count}")

            if current_count > 0:
                print(f"\n⚠️  WARNING: Database already contains {current_count} books")
                proceed = input("Continue with seeding? This will add more books. (y/N): ")
                if proceed.lower() != "y":
                    print("❌ Seeding cancelled by user")
                    return

            total_isbns = len(SEED_BOOK_ISBNS)
            print(f"\n🔍 Fetching metadata for {total_isbns} books from Open Library API...")
            print("-" * 60)

            created_count = 0
            skipped_count = 0
            failed_count = 0

            for index, isbn in enumerate(SEED_BOOK_ISBNS, 1):
                progress = f"[{index}/{total_isbns}]"

                book_data = await fetch_book_metadata(isbn)

                if book_data is None:
                    print(f"{progress} ⚠️  Failed to fetch: ISBN {isbn}")
                    failed_count += 1
                    await asyncio.sleep(OPEN_LIBRARY_RATE_LIMIT_DELAY_SECONDS)
                    continue

                existing = await db.execute(select(Book).where(Book.isbn == book_data["isbn"]))
                if existing.scalar_one_or_none():
                    print(f"{progress} ⏭️  Skipped: {book_data['title'][:40]}... (exists)")
                    skipped_count += 1
                    await asyncio.sleep(OPEN_LIBRARY_RATE_LIMIT_DELAY_SECONDS)
                    continue

                book = Book(**book_data)
                db.add(book)
                print(f"{progress} ✅ Added: {book_data['title'][:50]} by {book_data['author'][:30]}")
                created_count += 1

                await asyncio.sleep(OPEN_LIBRARY_RATE_LIMIT_DELAY_SECONDS)

                if index % 10 == 0:
                    await db.commit()
                    print(f"\n💾 Progress saved (committed {index} books)\n")

            await db.commit()

            print("\n" + "=" * 60)
            print("✨ SEEDING COMPLETE!")
            print("=" * 60)
            print(f"📚 Created:  {created_count} book(s)")
            print(f"⏭️  Skipped:  {skipped_count} book(s)")
            print(f"⚠️  Failed:   {failed_count} book(s)")
            print(f"📊 Total:    {created_count + current_count} book(s) now in database")
            print("=" * 60)

        except Exception as e:
            await db.rollback()
            print(f"\n❌ Error during seeding: {e}")
            raise


if __name__ == "__main__":
    asyncio.run(seed_production())
