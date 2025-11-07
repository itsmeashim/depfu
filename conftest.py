"""
Global pytest configuration and fixtures
"""
import pytest
import tempfile
import shutil
import os
import sys

# Add the project root to the path
sys.path.insert(0, os.path.dirname(__file__))


@pytest.fixture
def temp_directory():
    """Create a temporary directory for tests"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def sample_dependencies():
    """Sample dependency dictionary for testing"""
    return {
        "express": "^4.18.0",
        "lodash": "^4.17.21",
        "fake-package": "^1.0.0",
        "another-fake": "^2.0.0"
    }


@pytest.fixture
def mock_session():
    """Mock requests session for testing"""
    from unittest.mock import MagicMock
    return MagicMock()


def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "npm: NPM provider tests")
    config.addinivalue_line("markers", "pypi: PyPI provider tests")
    config.addinivalue_line("markers", "cargo: Cargo provider tests")
    config.addinivalue_line("markers", "go: Go provider tests")
    config.addinivalue_line("markers", "maven: Maven provider tests")
    config.addinivalue_line("markers", "gradle: Gradle provider tests")
    config.addinivalue_line("markers", "rubygems: RubyGems provider tests")
    config.addinivalue_line("markers", "slow: Slow running tests")
    config.addinivalue_line("markers", "network: Tests that require network access")