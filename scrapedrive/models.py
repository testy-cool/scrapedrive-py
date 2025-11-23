"""Data models for ScrapeDrive SDK."""

from dataclasses import dataclass
from typing import Optional, Dict, Any
from enum import Enum


class ScrapeStatus(str, Enum):
    """Status of a scraping job."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class ScrapeResult:
    """Result of a scraping job.

    Attributes:
        id: Unique job identifier
        status: Current status of the scraping job
        url: Original URL that was scraped
        html: Raw HTML content (if requested)
        markdown: Markdown-converted content (if requested)
        screenshot: Screenshot URL or data (if available)
        final_url: Final URL after redirects
        status_code: HTTP status code
        headers: HTTP response headers
        credits: Credits consumed for this request
        attempts: Number of retry attempts
        error: Error message (if failed)
        metadata: Additional metadata
    """

    id: str
    status: ScrapeStatus
    url: str
    html: Optional[str] = None
    markdown: Optional[str] = None
    screenshot: Optional[str] = None
    final_url: Optional[str] = None
    status_code: Optional[int] = None
    headers: Optional[Dict[str, str]] = None
    credits: Optional[int] = None
    attempts: Optional[int] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    @property
    def is_completed(self) -> bool:
        """Check if scraping is completed."""
        return self.status == ScrapeStatus.COMPLETED

    @property
    def is_failed(self) -> bool:
        """Check if scraping failed."""
        return self.status == ScrapeStatus.FAILED

    @property
    def is_pending(self) -> bool:
        """Check if scraping is pending or processing."""
        return self.status in (ScrapeStatus.PENDING, ScrapeStatus.PROCESSING)

    @property
    def success(self) -> bool:
        """Check if scraping succeeded (completed with 2xx status code)."""
        return self.is_completed and self.status_code and 200 <= self.status_code < 300

    def __repr__(self) -> str:
        return f"ScrapeResult(id={self.id!r}, status={self.status.value!r}, url={self.url!r})"
