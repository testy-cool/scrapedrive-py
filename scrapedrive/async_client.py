"""Asynchronous client for ScrapeDrive API."""

import os
import asyncio
from typing import Optional, Dict, Any
import html2text

try:
    import aiohttp
except ImportError:
    aiohttp = None

from scrapedrive.models import ScrapeResult, ScrapeStatus
from scrapedrive.exceptions import (
    AuthenticationError,
    RateLimitError,
    ScrapingError,
    TimeoutError,
)


class AsyncScrapeDrive:
    """Asynchronous client for ScrapeDrive API.

    Requires 'aiohttp' to be installed: pip install scrapedrive[async]

    Example:
        >>> async with AsyncScrapeDrive(api_key="your-api-key") as client:
        ...     result = await client.scrape("https://example.com")
        ...     print(result.markdown)
    """

    BASE_URL = "https://api.scrapedrive.com/api"

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: int = 300,
        poll_interval: float = 2.0,
    ):
        """Initialize AsyncScrapeDrive client.

        Args:
            api_key: API key for authentication. If not provided, looks for
                SCRAPEDRIVE_API_KEY environment variable.
            base_url: Base URL for API. Defaults to production API.
            timeout: Maximum time to wait for scraping to complete (seconds).
            poll_interval: Time to wait between status checks (seconds).

        Raises:
            AuthenticationError: If no API key is provided.
            ImportError: If aiohttp is not installed.
        """
        if aiohttp is None:
            raise ImportError(
                "aiohttp is required for async client. "
                "Install it with: pip install scrapedrive[async]"
            )

        self.api_key = api_key or os.getenv("SCRAPEDRIVE_API_KEY")
        if not self.api_key:
            raise AuthenticationError(
                "API key is required. Provide it via api_key parameter or "
                "SCRAPEDRIVE_API_KEY environment variable."
            )

        self.base_url = base_url or self.BASE_URL
        self.timeout = timeout
        self.poll_interval = poll_interval
        self._session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        """Support for async context manager."""
        await self._ensure_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Close session when exiting context."""
        await self.close()

    async def _ensure_session(self):
        """Ensure session is created."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                }
            )

    async def close(self):
        """Close the HTTP session."""
        if self._session and not self._session.closed:
            await self._session.close()

    def _ensure_https(self, url: str) -> str:
        """Ensure URL uses HTTPS."""
        if url.startswith("https://"):
            return url
        elif url.startswith("http://"):
            return "https://" + url[len("http://") :]
        else:
            return "https://" + url

    async def _handle_response(self, response: aiohttp.ClientResponse) -> Dict[str, Any]:
        """Handle API response and raise appropriate exceptions."""
        if response.status == 401:
            raise AuthenticationError("Invalid API key")
        elif response.status == 429:
            raise RateLimitError("Rate limit exceeded")
        elif response.status >= 400:
            try:
                error_data = await response.json()
                message = error_data.get("error", f"HTTP {response.status}")
            except Exception:
                text = await response.text()
                message = f"HTTP {response.status}: {text}"
            raise ScrapingError(message, details={"status_code": response.status})

        return await response.json()

    async def scrape(
        self,
        url: str,
        *,
        render_js: bool = True,
        proxy_residential: bool = True,
        proxy_country: str = "US",
        wait_for_completion: bool = True,
        return_markdown: bool = True,
        return_html: bool = False,
    ) -> ScrapeResult:
        """Scrape a URL asynchronously.

        Args:
            url: URL to scrape.
            render_js: Whether to render JavaScript.
            proxy_residential: Whether to use residential proxies.
            proxy_country: Proxy country code (e.g., "US", "GB").
            wait_for_completion: If True, wait for scraping to complete.
                If False, return immediately with job ID.
            return_markdown: Convert HTML to markdown.
            return_html: Include raw HTML in result.

        Returns:
            ScrapeResult: Result of the scraping job.

        Raises:
            ScrapingError: If scraping fails.
            TimeoutError: If scraping times out.

        Example:
            >>> result = await client.scrape("https://example.com")
            >>> print(result.markdown)

            >>> result = await client.scrape(
            ...     "https://example.com",
            ...     render_js=False,
            ...     proxy_country="GB"
            ... )
        """
        await self._ensure_session()
        url = self._ensure_https(url)

        # Submit scraping job
        async with self._session.post(
            f"{self.base_url}/scrape/async",
            json={
                "url": url,
                "render_js": render_js,
                "proxy_residential": proxy_residential,
                "proxy_country": proxy_country,
            },
        ) as response:
            data = await self._handle_response(response)

        job_id = data.get("id")
        status_url = data.get("status_url")

        if not wait_for_completion:
            return ScrapeResult(
                id=job_id,
                status=ScrapeStatus.PENDING,
                url=url,
            )

        # Poll for completion
        start_time = asyncio.get_event_loop().time()
        while True:
            if asyncio.get_event_loop().time() - start_time > self.timeout:
                raise TimeoutError(
                    f"Scraping timed out after {self.timeout} seconds"
                )

            async with self._session.get(status_url) as status_response:
                result = await self._handle_response(status_response)

            status = result.get("status")

            if status == "completed":
                response_data = result.get("response", {})
                html_body = response_data.get("body", "")
                markdown = None

                if return_markdown and html_body:
                    h = html2text.HTML2Text()
                    h.ignore_links = False
                    markdown = h.handle(html_body)

                return ScrapeResult(
                    id=job_id,
                    status=ScrapeStatus.COMPLETED,
                    url=result.get("url", url),
                    html=html_body if return_html else None,
                    markdown=markdown,
                    final_url=response_data.get("final_url"),
                    status_code=response_data.get("status_code"),
                    headers=response_data.get("headers"),
                    credits=response_data.get("credits"),
                    attempts=result.get("attempts"),
                    screenshot=response_data.get("screenshot"),
                    metadata=response_data,
                )

            elif status == "failed":
                error_msg = result.get("error", "Scraping failed")
                raise ScrapingError(error_msg, details=result)

            await asyncio.sleep(self.poll_interval)

    async def get_status(self, job_id: str, status_url: str) -> ScrapeResult:
        """Get status of a scraping job.

        Args:
            job_id: Job ID.
            status_url: Status URL returned from initial scrape request.

        Returns:
            ScrapeResult: Current status of the job.

        Example:
            >>> result = await client.scrape("https://example.com", wait_for_completion=False)
            >>> # ... do other work ...
            >>> final_result = await client.get_status(result.id, status_url)
        """
        await self._ensure_session()

        async with self._session.get(status_url) as response:
            result = await self._handle_response(response)

        status = result.get("status", "pending")
        response_data = result.get("response", {})
        html_body = response_data.get("body", "")

        return ScrapeResult(
            id=job_id,
            status=ScrapeStatus(status),
            url=result.get("url", ""),
            html=html_body if html_body else None,
            final_url=response_data.get("final_url"),
            status_code=response_data.get("status_code"),
            headers=response_data.get("headers"),
            credits=response_data.get("credits"),
            attempts=result.get("attempts"),
            screenshot=response_data.get("screenshot"),
            metadata=response_data,
        )
