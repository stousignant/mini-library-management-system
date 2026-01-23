"""Quick test script to verify OpenRouter API key and connection."""

import asyncio
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

api_key = os.getenv("OPENROUTER_API_KEY")
print(f"API Key loaded: {api_key[:20]}..." if api_key else "API Key NOT loaded!")
print(f"API Key starts with sk-or-v1-: {api_key.startswith('sk-or-v1-') if api_key else 'N/A'}")

from app.services.ai_service import generate_book_summary  # noqa: E402


async def test():
    print("\nTesting OpenRouter connection...")
    summary = await generate_book_summary(title="Test Book", author="Test Author", isbn="1234567890")
    if summary:
        print(f"✅ Success! Generated summary:\n{summary}")
    else:
        print("❌ Failed to generate summary")


if __name__ == "__main__":
    asyncio.run(test())
