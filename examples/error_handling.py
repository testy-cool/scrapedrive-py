"""Error handling examples for ScrapeDrive SDK."""

from scrapedrive import (
    ScrapeDrive,
    ScrapingError,
    TimeoutError,
    AuthenticationError,
    RateLimitError,
)

# Example 1: Basic error handling
print("Example 1: Basic error handling")
try:
    with ScrapeDrive(api_key="invalid-key") as client:
        result = client.scrape("https://example.com")
except AuthenticationError as e:
    print(f"Authentication failed: {e}")

# Example 2: Timeout handling
print("\nExample 2: Timeout handling")
try:
    with ScrapeDrive() as client:
        result = client.scrape(
            "https://example.com",
            timeout=5  # Very short timeout for demo
        )
except TimeoutError as e:
    print(f"Request timed out: {e}")

# Example 3: Comprehensive error handling
print("\nExample 3: Comprehensive error handling")
with ScrapeDrive() as client:
    try:
        result = client.scrape("https://example.com")

        if result.is_completed:
            print(f"Success! Got {len(result.markdown)} characters")
        elif result.is_failed:
            print(f"Scraping failed: {result.error}")

    except AuthenticationError:
        print("Check your API key!")
    except RateLimitError:
        print("Rate limit exceeded. Please wait before retrying.")
    except TimeoutError:
        print("Request took too long. Try increasing the timeout.")
    except ScrapingError as e:
        print(f"Scraping error: {e}")
        if hasattr(e, 'details'):
            print(f"Details: {e.details}")
    except Exception as e:
        print(f"Unexpected error: {e}")
