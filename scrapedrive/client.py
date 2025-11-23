"""Synchronous client for ScrapeDrive API."""

import os
import time
from typing import Optional, Dict, Any
import requests
import html2text

from scrapedrive.models import ScrapeResult, ScrapeStatus
from scrapedrive.exceptions import (
    AuthenticationError,
    RateLimitError,
    ScrapingError,
    TimeoutError,
)


class ScrapeDrive:
    """Synchronous client for ScrapeDrive API.

    Example:
        >>> client = ScrapeDrive(api_key="your-api-key")
        >>> result = client.scrape("https://example.com")
        >>> print(result.markdown)

    Or using context manager:
        >>> with ScrapeDrive(api_key="your-api-key") as client:
        ...     result = client.scrape("https://example.com")
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
        """Initialize ScrapeDrive client.

        Args:
            api_key: API key for authentication. If not provided, looks for
                SCRAPEDRIVE_API_KEY environment variable.
            base_url: Base URL for API. Defaults to production API.
            timeout: Maximum time to wait for scraping to complete (seconds).
            poll_interval: Time to wait between status checks (seconds).

        Raises:
            AuthenticationError: If no API key is provided.
        """
        self.api_key = api_key or os.getenv("SCRAPEDRIVE_API_KEY")
        if not self.api_key:
            raise AuthenticationError(
                "API key is required. Provide it via api_key parameter or "
                "SCRAPEDRIVE_API_KEY environment variable."
            )

        self.base_url = base_url or self.BASE_URL
        self.timeout = timeout
        self.poll_interval = poll_interval
        self._session = requests.Session()
        self._session.headers.update(
            {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
        )

    def __enter__(self):
        """Support for context manager."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Close session when exiting context."""
        self.close()

    def close(self):
        """Close the HTTP session."""
        self._session.close()

    def _ensure_https(self, url: str) -> str:
        """Ensure URL uses HTTPS."""
        if url.startswith("https://"):
            return url
        elif url.startswith("http://"):
            return "https://" + url[len("http://") :]
        else:
            return "https://" + url

    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """Handle API response and raise appropriate exceptions."""
        if response.status_code == 401:
            raise AuthenticationError("Invalid API key")
        elif response.status_code == 429:
            raise RateLimitError("Rate limit exceeded")
        elif response.status_code >= 400:
            try:
                error_data = response.json()
                message = error_data.get("error", f"HTTP {response.status_code}")
            except Exception:
                message = f"HTTP {response.status_code}: {response.text}"
            raise ScrapingError(message, details={"status_code": response.status_code})

        return response.json()

    def scrape(
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
        """Scrape a URL.

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
            >>> result = client.scrape("https://example.com")
            >>> print(result.markdown)

            >>> result = client.scrape(
            ...     "https://example.com",
            ...     render_js=False,
            ...     proxy_country="GB"
            ... )
        """
        url = self._ensure_https(url)

        # Submit scraping job
        response = self._session.post(
            f"{self.base_url}/scrape/async",
            json={
                "url": url,
                "render_js": render_js,
                "proxy_residential": proxy_residential,
                "proxy_country": proxy_country,
            },
        )

        data = self._handle_response(response)
        job_id = data.get("id")
        status_url = data.get("status_url")

        if not wait_for_completion:
            return ScrapeResult(
                id=job_id,
                status=ScrapeStatus.PENDING,
                url=url,
            )

        # Poll for completion
        start_time = time.time()
        while True:
            if time.time() - start_time > self.timeout:
                raise TimeoutError(
                    f"Scraping timed out after {self.timeout} seconds"
                )

            status_response = self._session.get(status_url)
            result = self._handle_response(status_response)

            status = result.get("status")

            if status == "completed":
                html_body = result.get("response", {}).get("body", "")
                markdown = None

                if return_markdown and html_body:
                    h = html2text.HTML2Text()
                    h.ignore_links = False
                    markdown = h.handle(html_body)

                return ScrapeResult(
                    id=job_id,
                    status=ScrapeStatus.COMPLETED,
                    url=url,
                    html=html_body if return_html else None,
                    markdown=markdown,
                    metadata=result.get("response", {}),
                )

            elif status == "failed":
                error_msg = result.get("error", "Scraping failed")
                raise ScrapingError(error_msg, details=result)

            time.sleep(self.poll_interval)

    def get_status(self, job_id: str, status_url: str) -> ScrapeResult:
        """Get status of a scraping job.

        Args:
            job_id: Job ID.
            status_url: Status URL returned from initial scrape request.

        Returns:
            ScrapeResult: Current status of the job.

        Example:
            >>> result = client.scrape("https://example.com", wait_for_completion=False)
            >>> # ... do other work ...
            >>> final_result = client.get_status(result.id, status_url)
        """
        response = self._session.get(status_url)
        result = self._handle_response(response)

        status = result.get("status", "pending")
        html_body = result.get("response", {}).get("body", "")

        return ScrapeResult(
            id=job_id,
            status=ScrapeStatus(status),
            url=result.get("url", ""),
            html=html_body if html_body else None,
            metadata=result.get("response", {}),
        )
