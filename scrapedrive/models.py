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
    """Result of a scraping job."""

    id: str
    status: ScrapeStatus
    url: str
    html: Optional[str] = None
    markdown: Optional[str] = None
    screenshot: Optional[str] = None
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

    def __repr__(self) -> str:
        return f"ScrapeResult(id={self.id!r}, status={self.status.value!r}, url={self.url!r})"
