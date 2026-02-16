"""Root conftest for pytest - shared fixtures and configuration."""

import pytest


def pytest_configure(config):
    """Configure pytest with custom settings."""
    # Register custom markers
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "slow: Slow tests")
    config.addinivalue_line("markers", "api: API tests")
    config.addinivalue_line("markers", "db: Database tests")
    config.addinivalue_line("markers", "ai: AI service tests")
