"""
Database seeding script for books.

Fetches book metadata from the Open Library API and populates
the database with high-quality book data including cover images.
"""

import asyncio
import sys
from pathlib import Path

import httpx

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
                print(f"   ⚠️  No data found for ISBN {isbn}")
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

    except httpx.HTTPError as e:
        print(f"   ⚠️  HTTP error fetching ISBN {isbn}: {e}")
        return None
    except Exception as e:
        print(f"   ⚠️  Error fetching ISBN {isbn}: {e}")
        return None


async def seed_database() -> None:
    """
    Seed the database with book data from Open Library API.

    Fetches metadata for all books in SEED_BOOK_ISBNS and creates
    database entries if they don't already exist.
    """
    print("🌱 Seeding database with Open Library data...")

    async with AsyncSessionLocal() as db:
        try:
            created_count = 0
            skipped_count = 0
            total_isbns = len(SEED_BOOK_ISBNS)

            for index, isbn in enumerate(SEED_BOOK_ISBNS, 1):
                print(f"   [{index}/{total_isbns}] Fetching ISBN {isbn}...")

                book_data = await fetch_book_metadata(isbn)

                if book_data is None:
                    skipped_count += 1
                    await asyncio.sleep(OPEN_LIBRARY_RATE_LIMIT_DELAY_SECONDS)
                    continue

                existing_book = await db.execute(Book.__table__.select().where(Book.isbn == book_data["isbn"]))
                if existing_book.scalar_one_or_none():
                    print(f"   ⏭️  Skipped: {book_data['title']} (already exists)")
                    skipped_count += 1
                    await asyncio.sleep(OPEN_LIBRARY_RATE_LIMIT_DELAY_SECONDS)
                    continue

                book = Book(**book_data)
                db.add(book)
                print(f"   ✅ Added: {book_data['title']} by {book_data['author']}")
                created_count += 1

                await asyncio.sleep(OPEN_LIBRARY_RATE_LIMIT_DELAY_SECONDS)

            await db.commit()

            print("\n✨ Seeding complete!")
            print(f"   Created: {created_count} book(s)")
            print(f"   Skipped: {skipped_count} book(s)")

        except Exception as e:
            await db.rollback()
            print(f"\n❌ Error seeding database: {e}")
            raise


if __name__ == "__main__":
    asyncio.run(seed_database())
