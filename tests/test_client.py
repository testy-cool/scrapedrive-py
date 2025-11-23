"""Tests for synchronous ScrapeDrive client."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from scrapedrive import ScrapeDrive, ScrapeResult, ScrapeStatus
from scrapedrive.exceptions import (
    AuthenticationError,
    RateLimitError,
    ScrapingError,
    TimeoutError,
)


class TestScrapeDriveInit:
    """Test client initialization."""

    def test_init_with_api_key(self):
        """Test initialization with API key."""
        client = ScrapeDrive(api_key="test-key")
        assert client.api_key == "test-key"
        assert client.timeout == 300
        assert client.poll_interval == 2.0

    def test_init_with_env_var(self, monkeypatch):
        """Test initialization with environment variable."""
        monkeypatch.setenv("SCRAPEDRIVE_API_KEY", "env-key")
        client = ScrapeDrive()
        assert client.api_key == "env-key"

    def test_init_without_api_key(self, monkeypatch):
        """Test initialization fails without API key."""
        monkeypatch.delenv("SCRAPEDRIVE_API_KEY", raising=False)
        with pytest.raises(AuthenticationError):
            ScrapeDrive()

    def test_init_custom_params(self):
        """Test initialization with custom parameters."""
        client = ScrapeDrive(
            api_key="test-key",
            timeout=600,
            poll_interval=5.0,
        )
        assert client.timeout == 600
        assert client.poll_interval == 5.0

    def test_context_manager(self):
        """Test context manager support."""
        with ScrapeDrive(api_key="test-key") as client:
            assert client.api_key == "test-key"


class TestEnsureHttps:
    """Test URL normalization."""

    def test_https_url(self):
        """Test HTTPS URL remains unchanged."""
        client = ScrapeDrive(api_key="test-key")
        url = client._ensure_https("https://example.com")
        assert url == "https://example.com"

    def test_http_url(self):
        """Test HTTP URL is converted to HTTPS."""
        client = ScrapeDrive(api_key="test-key")
        url = client._ensure_https("http://example.com")
        assert url == "https://example.com"

    def test_no_protocol_url(self):
        """Test URL without protocol gets HTTPS added."""
        client = ScrapeDrive(api_key="test-key")
        url = client._ensure_https("example.com")
        assert url == "https://example.com"


class TestScrape:
    """Test scraping functionality."""

    @patch("scrapedrive.client.requests.Session")
    def test_scrape_success(self, mock_session_class):
        """Test successful scraping."""
        # Mock session
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session

        # Mock initial POST response
        post_response = Mock()
        post_response.status_code = 200
        post_response.json.return_value = {
            "id": "job-123",
            "status_url": "https://api.scrapedrive.com/status/job-123",
        }
        mock_session.post.return_value = post_response

        # Mock status GET response
        get_response = Mock()
        get_response.status_code = 200
        get_response.json.return_value = {
            "status": "completed",
            "response": {
                "body": "<html><body>Test</body></html>",
            },
        }
        mock_session.get.return_value = get_response

        # Test scraping
        client = ScrapeDrive(api_key="test-key")
        result = client.scrape("https://example.com")

        assert result.id == "job-123"
        assert result.status == ScrapeStatus.COMPLETED
        assert result.markdown is not None
        assert "Test" in result.markdown

    @patch("scrapedrive.client.requests.Session")
    def test_scrape_without_waiting(self, mock_session_class):
        """Test scraping without waiting for completion."""
        # Mock session
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session

        # Mock POST response
        post_response = Mock()
        post_response.status_code = 200
        post_response.json.return_value = {
            "id": "job-123",
            "status_url": "https://api.scrapedrive.com/status/job-123",
        }
        mock_session.post.return_value = post_response

        # Test scraping
        client = ScrapeDrive(api_key="test-key")
        result = client.scrape("https://example.com", wait_for_completion=False)

        assert result.id == "job-123"
        assert result.status == ScrapeStatus.PENDING
        mock_session.get.assert_not_called()

    @patch("scrapedrive.client.requests.Session")
    def test_scrape_failed(self, mock_session_class):
        """Test failed scraping."""
        # Mock session
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session

        # Mock POST response
        post_response = Mock()
        post_response.status_code = 200
        post_response.json.return_value = {
            "id": "job-123",
            "status_url": "https://api.scrapedrive.com/status/job-123",
        }
        mock_session.post.return_value = post_response

        # Mock status response showing failure
        get_response = Mock()
        get_response.status_code = 200
        get_response.json.return_value = {
            "status": "failed",
            "error": "Failed to scrape",
        }
        mock_session.get.return_value = get_response

        # Test scraping
        client = ScrapeDrive(api_key="test-key")
        with pytest.raises(ScrapingError) as exc_info:
            client.scrape("https://example.com")

        assert "Failed to scrape" in str(exc_info.value)

    @patch("scrapedrive.client.requests.Session")
    def test_authentication_error(self, mock_session_class):
        """Test authentication error handling."""
        # Mock session
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session

        # Mock 401 response
        post_response = Mock()
        post_response.status_code = 401
        mock_session.post.return_value = post_response

        # Test scraping
        client = ScrapeDrive(api_key="invalid-key")
        with pytest.raises(AuthenticationError):
            client.scrape("https://example.com")

    @patch("scrapedrive.client.requests.Session")
    def test_rate_limit_error(self, mock_session_class):
        """Test rate limit error handling."""
        # Mock session
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session

        # Mock 429 response
        post_response = Mock()
        post_response.status_code = 429
        mock_session.post.return_value = post_response

        # Test scraping
        client = ScrapeDrive(api_key="test-key")
        with pytest.raises(RateLimitError):
            client.scrape("https://example.com")


class TestScrapeResult:
    """Test ScrapeResult model."""

    def test_is_completed(self):
        """Test is_completed property."""
        result = ScrapeResult(
            id="job-123",
            status=ScrapeStatus.COMPLETED,
            url="https://example.com",
        )
        assert result.is_completed is True
        assert result.is_failed is False
        assert result.is_pending is False

    def test_is_failed(self):
        """Test is_failed property."""
        result = ScrapeResult(
            id="job-123",
            status=ScrapeStatus.FAILED,
            url="https://example.com",
        )
        assert result.is_completed is False
        assert result.is_failed is True
        assert result.is_pending is False

    def test_is_pending(self):
        """Test is_pending property."""
        result = ScrapeResult(
            id="job-123",
            status=ScrapeStatus.PENDING,
            url="https://example.com",
        )
        assert result.is_completed is False
        assert result.is_failed is False
        assert result.is_pending is True
