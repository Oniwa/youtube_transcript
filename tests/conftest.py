"""
conftest.py — pytest configuration for the youtube_transcript test suite.

Registers custom markers so that pytest does not emit PytestUnknownMarkWarning.
"""
import pytest


def pytest_configure(config: pytest.Config) -> None:
    """Register custom pytest markers.

    Args:
        config: The pytest configuration object.
    """
    config.addinivalue_line(
        "markers",
        "integration: marks tests as integration tests that make real network calls",
    )
