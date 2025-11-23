# ScrapeDrive Python SDK

[![PyPI version](https://badge.fury.io/py/scrapedrive.svg)](https://badge.fury.io/py/scrapedrive)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An ergonomic Python SDK for the [ScrapeDrive](https://scrapedrive.com) API - making web scraping simple and powerful.

## Features

- 🚀 **Simple & Intuitive API** - Get started with just a few lines of code
- ⚡ **Async Support** - Built-in support for asyncio with `AsyncScrapeDrive`
- 🔄 **Automatic Polling** - No need to manually check job status
- 🛡️ **Type Hints** - Full type annotations for better IDE support
- 📦 **Response Models** - Clean, structured response objects
- 🎯 **Smart Defaults** - Sensible defaults with easy customization
- 🔐 **Environment Variable Support** - Flexible API key configuration
- ✨ **Context Manager Support** - Proper resource management

## Installation

```bash
pip install scrapedrive
```

For async support, install with the async extra:

```bash
pip install scrapedrive[async]
```

## Quick Start

### Synchronous Usage

```python
from scrapedrive import ScrapeDrive

# Initialize the client
client = ScrapeDrive(api_key="your-api-key")

# Scrape a website
result = client.scrape("https://example.com")

# Access the results
print(result.markdown)  # Markdown version
print(result.html)      # Raw HTML (if requested)
print(result.status)    # Job status
```

### Using Context Manager (Recommended)

```python
from scrapedrive import ScrapeDrive

with ScrapeDrive(api_key="your-api-key") as client:
    result = client.scrape("https://example.com")
    print(result.markdown)
```

### Async Usage

```python
import asyncio
from scrapedrive import AsyncScrapeDrive

async def main():
    async with AsyncScrapeDrive(api_key="your-api-key") as client:
        result = await client.scrape("https://example.com")
        print(result.markdown)

asyncio.run(main())
```

## Configuration

### API Key

You can provide your API key in three ways:

1. **Direct parameter**:
   ```python
   client = ScrapeDrive(api_key="your-api-key")
   ```

2. **Environment variable**:
   ```bash
   export SCRAPEDRIVE_API_KEY="your-api-key"
   ```
   ```python
   client = ScrapeDrive()  # Automatically uses env var
   ```

3. **`.env` file** (requires `python-dotenv`):
   ```bash
   # .env
   SCRAPEDRIVE_API_KEY=your-api-key
   ```

### Advanced Options

```python
client = ScrapeDrive(
    api_key="your-api-key",
    timeout=300,        # Max time to wait for completion (seconds)
    poll_interval=2.0,  # Time between status checks (seconds)
)

result = client.scrape(
    "https://example.com",
    render_js=True,            # Render JavaScript
    proxy_residential=True,    # Use residential proxies
    proxy_country="US",        # Proxy country code
    return_markdown=True,      # Convert to markdown
    return_html=True,          # Also return raw HTML
    wait_for_completion=True,  # Wait for job to complete
)
```

## Examples

### Basic Scraping

```python
from scrapedrive import ScrapeDrive

with ScrapeDrive() as client:
    result = client.scrape("https://news.ycombinator.com")
    print(result.markdown)
```

### Custom Configuration

```python
from scrapedrive import ScrapeDrive

with ScrapeDrive() as client:
    result = client.scrape(
        "https://example.com",
        render_js=False,           # Don't render JavaScript
        proxy_country="GB",        # Use UK proxies
        return_html=True,          # Get raw HTML too
    )

    print(f"Status: {result.status}")
    print(f"Markdown length: {len(result.markdown)}")
    print(f"HTML length: {len(result.html)}")
```

### Non-blocking Scraping

```python
from scrapedrive import ScrapeDrive

with ScrapeDrive() as client:
    # Start scraping without waiting
    result = client.scrape(
        "https://example.com",
        wait_for_completion=False
    )

    print(f"Job ID: {result.id}")
    print(f"Status: {result.status}")

    # Do other work...

    # Check status later
    final_result = client.get_status(result.id, status_url)
    if final_result.is_completed:
        print(final_result.markdown)
```

### Async Batch Scraping

```python
import asyncio
from scrapedrive import AsyncScrapeDrive

async def scrape_multiple(urls):
    async with AsyncScrapeDrive() as client:
        tasks = [client.scrape(url) for url in urls]
        results = await asyncio.gather(*tasks)
        return results

urls = [
    "https://example.com",
    "https://example.org",
    "https://example.net",
]

results = asyncio.run(scrape_multiple(urls))
for result in results:
    print(f"{result.url}: {len(result.markdown)} chars")
```

### Error Handling

```python
from scrapedrive import ScrapeDrive, ScrapingError, TimeoutError

with ScrapeDrive() as client:
    try:
        result = client.scrape("https://example.com", timeout=60)
        print(result.markdown)
    except TimeoutError:
        print("Scraping took too long!")
    except ScrapingError as e:
        print(f"Scraping failed: {e}")
        print(f"Details: {e.details}")
```

## Response Object

The `ScrapeResult` object provides easy access to scraping results:

```python
result = client.scrape("https://example.com")

# Core Properties
result.id           # Job ID
result.status       # ScrapeStatus enum (pending, processing, completed, failed)
result.url          # Original URL that was scraped
result.final_url    # Final URL after redirects

# Content
result.markdown     # Markdown-converted content
result.html         # Raw HTML (if requested with return_html=True)
result.screenshot   # Screenshot data/URL (if available)

# Response Details
result.status_code  # HTTP status code (e.g., 200, 404)
result.headers      # HTTP response headers dict
result.credits      # Credits consumed for this request
result.attempts     # Number of retry attempts made

# Additional Data
result.metadata     # Additional response metadata
result.error        # Error message (if failed)

# Helper Properties
result.is_completed  # True if scraping completed
result.is_failed     # True if scraping failed
result.is_pending    # True if still processing
result.success       # True if completed with 2xx status code
```

### Accessing Response Data

```python
result = client.scrape("https://example.com")

# Check if successful
if result.success:
    print(f"Successfully scraped {result.final_url}")
    print(f"Status: {result.status_code}")
    print(f"Credits used: {result.credits}")
    print(f"Content length: {len(result.markdown)}")

# Access headers
if result.headers:
    content_type = result.headers.get("content-type")
    print(f"Content-Type: {content_type}")
```

## Error Handling

The SDK provides specific exceptions for different error cases:

- `ScrapeDriveError` - Base exception for all errors
- `AuthenticationError` - Invalid or missing API key
- `RateLimitError` - Rate limit exceeded
- `ScrapingError` - Scraping job failed
- `TimeoutError` - Request timed out

## Development

### Setting Up Development Environment

```bash
# Clone the repository
git clone https://github.com/yourusername/scrapedrive-py.git
cd scrapedrive-py

# Install in development mode with all extras
pip install -e ".[dev,async]"

# Run tests
pytest

# Run linting
ruff check .

# Format code
black .
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=scrapedrive --cov-report=html

# Run specific test file
pytest tests/test_client.py
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Links

- [Documentation](https://docs.scrapedrive.com)
- [API Reference](https://api.scrapedrive.com/docs)
- [GitHub Repository](https://github.com/yourusername/scrapedrive-py)
- [Issue Tracker](https://github.com/yourusername/scrapedrive-py/issues)

## Support

If you encounter any issues or have questions:

1. Check the [documentation](https://docs.scrapedrive.com)
2. Search [existing issues](https://github.com/yourusername/scrapedrive-py/issues)
3. Open a [new issue](https://github.com/yourusername/scrapedrive-py/issues/new)
