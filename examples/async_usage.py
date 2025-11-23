"""Async usage examples for ScrapeDrive SDK."""

import asyncio
from scrapedrive import AsyncScrapeDrive

# Example 1: Basic async scraping
async def example_basic():
    print("Example 1: Basic async scraping")
    async with AsyncScrapeDrive(api_key="your-api-key") as client:
        result = await client.scrape("https://example.com")
        print(f"Successfully scraped {result.url}")
        print(f"Content length: {len(result.markdown)} characters")

# Example 2: Scrape multiple URLs concurrently
async def example_batch():
    print("\nExample 2: Batch scraping")
    urls = [
        "https://example.com",
        "https://example.org",
        "https://example.net",
    ]

    async with AsyncScrapeDrive() as client:
        tasks = [client.scrape(url) for url in urls]
        results = await asyncio.gather(*tasks)

        for result in results:
            print(f"{result.url}: {len(result.markdown)} chars")

# Example 3: With error handling
async def example_with_error_handling():
    print("\nExample 3: With error handling")
    from scrapedrive import ScrapingError, TimeoutError

    async with AsyncScrapeDrive() as client:
        try:
            result = await client.scrape(
                "https://example.com",
                timeout=60
            )
            print(f"Success: {result.url}")
        except TimeoutError:
            print("Scraping took too long!")
        except ScrapingError as e:
            print(f"Scraping failed: {e}")

# Run examples
if __name__ == "__main__":
    asyncio.run(example_basic())
    asyncio.run(example_batch())
    asyncio.run(example_with_error_handling())
