"""Pytest configuration and fixtures."""

import pytest


@pytest.fixture
def mock_api_key():
    """Provide a mock API key."""
    return "test-api-key-123"


@pytest.fixture
def sample_html():
    """Provide sample HTML for testing."""
    return """
    <html>
        <head><title>Test Page</title></head>
        <body>
            <h1>Hello World</h1>
            <p>This is a test page.</p>
        </body>
    </html>
    """


@pytest.fixture
def sample_scrape_response():
    """Provide a sample scrape API response."""
    return {
        "id": "job-123",
        "status": "completed",
        "url": "https://example.com",
        "response": {
            "body": "<html><body>Test</body></html>",
            "status_code": 200,
        },
    }
