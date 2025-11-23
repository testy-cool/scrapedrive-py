"""Tests for asynchronous ScrapeDrive client."""

import pytest
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from scrapedrive import AsyncScrapeDrive, ScrapeResult, ScrapeStatus
from scrapedrive.exceptions import (
    AuthenticationError,
    RateLimitError,
    ScrapingError,
)

# Skip all tests if aiohttp is not installed
pytest.importorskip("aiohttp")


class TestAsyncScrapeDriveInit:
    """Test async client initialization."""

    def test_init_with_api_key(self):
        """Test initialization with API key."""
        client = AsyncScrapeDrive(api_key="test-key")
        assert client.api_key == "test-key"
        assert client.timeout == 300
        assert client.poll_interval == 2.0

    def test_init_with_env_var(self, monkeypatch):
        """Test initialization with environment variable."""
        monkeypatch.setenv("SCRAPEDRIVE_API_KEY", "env-key")
        client = AsyncScrapeDrive()
        assert client.api_key == "env-key"

    def test_init_without_api_key(self, monkeypatch):
        """Test initialization fails without API key."""
        monkeypatch.delenv("SCRAPEDRIVE_API_KEY", raising=False)
        with pytest.raises(AuthenticationError):
            AsyncScrapeDrive()


class TestAsyncScrape:
    """Test async scraping functionality."""

    @pytest.mark.asyncio
    async def test_scrape_success(self):
        """Test successful async scraping."""
        client = AsyncScrapeDrive(api_key="test-key")

        # Mock aiohttp session
        mock_post_response = AsyncMock()
        mock_post_response.status = 200
        mock_post_response.json = AsyncMock(return_value={
            "id": "job-123",
            "status_url": "https://api.scrapedrive.com/status/job-123",
        })

        mock_get_response = AsyncMock()
        mock_get_response.status = 200
        mock_get_response.json = AsyncMock(return_value={
            "status": "completed",
            "response": {
                "body": "<html><body>Test</body></html>",
            },
        })

        mock_session = MagicMock()
        mock_session.post.return_value.__aenter__.return_value = mock_post_response
        mock_session.get.return_value.__aenter__.return_value = mock_get_response
        mock_session.closed = False

        client._session = mock_session

        # Test scraping
        result = await client.scrape("https://example.com")

        assert result.id == "job-123"
        assert result.status == ScrapeStatus.COMPLETED
        assert result.markdown is not None
        assert "Test" in result.markdown

        await client.close()

    @pytest.mark.asyncio
    async def test_scrape_without_waiting(self):
        """Test async scraping without waiting."""
        client = AsyncScrapeDrive(api_key="test-key")

        # Mock aiohttp session
        mock_post_response = AsyncMock()
        mock_post_response.status = 200
        mock_post_response.json = AsyncMock(return_value={
            "id": "job-123",
            "status_url": "https://api.scrapedrive.com/status/job-123",
        })

        mock_session = MagicMock()
        mock_session.post.return_value.__aenter__.return_value = mock_post_response
        mock_session.closed = False

        client._session = mock_session

        # Test scraping
        result = await client.scrape("https://example.com", wait_for_completion=False)

        assert result.id == "job-123"
        assert result.status == ScrapeStatus.PENDING

        await client.close()

    @pytest.mark.asyncio
    async def test_context_manager(self):
        """Test async context manager."""
        async with AsyncScrapeDrive(api_key="test-key") as client:
            assert client.api_key == "test-key"
