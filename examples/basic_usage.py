"""Basic usage examples for ScrapeDrive SDK."""

from scrapedrive import ScrapeDrive

# Example 1: Simple scraping
print("Example 1: Simple scraping")
with ScrapeDrive(api_key="your-api-key") as client:
    result = client.scrape("https://example.com")
    print(f"Successfully scraped {result.url}")
    print(f"Content length: {len(result.markdown)} characters")
    print(result.markdown[:200] + "...")

# Example 2: Custom configuration
print("\nExample 2: Custom configuration")
with ScrapeDrive() as client:  # Uses SCRAPEDRIVE_API_KEY env var
    result = client.scrape(
        "https://news.ycombinator.com",
        render_js=True,
        proxy_country="US",
        return_html=True,
    )
    print(f"Status: {result.status}")
    print(f"Has HTML: {result.html is not None}")
    print(f"Has Markdown: {result.markdown is not None}")

# Example 3: Non-blocking scraping
print("\nExample 3: Non-blocking scraping")
with ScrapeDrive() as client:
    # Start scraping without waiting
    result = client.scrape(
        "https://example.com",
        wait_for_completion=False
    )
    print(f"Job started: {result.id}")
    print(f"Initial status: {result.status}")
    # You can do other work here...
