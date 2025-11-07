"""
Unit tests for misc.py utilities
"""
import pytest
from unittest.mock import patch, MagicMock
import sys
import os
from time import sleep

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from utils.misc import dependency_exists, recover_dependencies
from tests.fixtures.mock_responses import MOCK_MAVEN_SEARCH_RESPONSE


class TestMiscUtilities:
    """Test cases for misc.py utility functions"""

    def setup_method(self):
        """Set up test fixtures"""
        self.mock_session = MagicMock()

    def test_dependency_exists_npm_success(self):
        """Test dependency_exists for NPM package that exists"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        self.mock_session.get.return_value = mock_response

        result = dependency_exists("express", "npm", self.mock_session)

        assert result is True
        self.mock_session.get.assert_called_once_with(
            "https://deps.dev/_/s/npm/p/express/v/",
            timeout=10
        )

    def test_dependency_exists_npm_not_found(self):
        """Test dependency_exists for NPM package that doesn't exist"""
        mock_response = MagicMock()
        mock_response.status_code = 404
        self.mock_session.get.return_value = mock_response

        result = dependency_exists("nonexistent-package", "npm", self.mock_session)

        assert result is False
        self.mock_session.get.assert_called_once_with(
            "https://deps.dev/_/s/npm/p/nonexistent-package/v/",
            timeout=10
        )

    def test_dependency_exists_gradle_success(self):
        """Test dependency_exists for Gradle package that exists"""
        mock_response = MagicMock()
        mock_response.json.return_value = MOCK_MAVEN_SEARCH_RESPONSE
        self.mock_session.get.return_value = mock_response

        result = dependency_exists("org.example:test-artifact", "gradle", self.mock_session)

        assert result == mock_response
        self.mock_session.get.assert_called_once_with(
            "https://search.maven.org/solrsearch/select?q=g:org.example+AND+a:test-artifact&core=gav&rows=20&wt=json",
            timeout=10
        )

    def test_dependency_exists_gradle_not_found(self):
        """Test dependency_exists for Gradle package that doesn't exist"""
        mock_response = MagicMock()
        mock_response.json.return_value = {"response": {"numFound": 0}}
        self.mock_session.get.return_value = mock_response

        result = dependency_exists("org.fake:nonexistent", "gradle", self.mock_session)

        assert result is None

    @patch('utils.misc.sleep')
    @patch('builtins.print')
    def test_dependency_exists_exception_handling(self, mock_print, mock_sleep):
        """Test dependency_exists exception handling and rate limiting"""
        self.mock_session.get.side_effect = Exception("Network error")

        result = dependency_exists("test-package", "npm", self.mock_session)

        assert result is None
        mock_print.assert_called_once_with("[-] We have been rate limited, going to sleep for 5 minutes.")
        mock_sleep.assert_called_once_with(300)

    def test_recover_dependencies_npm_success(self):
        """Test recover_dependencies for NPM package"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        self.mock_session.get.return_value = mock_response

        result = recover_dependencies("express", "4.18.0", "npm", self.mock_session)

        assert result == mock_response
        self.mock_session.get.assert_called_once_with(
            "https://deps.dev/_/s/npm/p/express/v/4.18.0/dependencies",
            timeout=10
        )

    def test_recover_dependencies_gradle_success(self):
        """Test recover_dependencies for Gradle package"""
        mock_response = MagicMock()
        mock_response.json.return_value = MOCK_MAVEN_SEARCH_RESPONSE
        self.mock_session.get.return_value = mock_response

        result = recover_dependencies("org.example:test-artifact", "1.0.0", "gradle", self.mock_session)

        assert result == mock_response
        self.mock_session.get.assert_called_once_with(
            "https://search.maven.org/solrsearch/select?q=g:org.example+AND+a:test-artifact+AND+v:1.0.0&core=gav&rows=20&wt=json",
            timeout=10
        )

    def test_recover_dependencies_gradle_not_found(self):
        """Test recover_dependencies for Gradle package that doesn't exist"""
        mock_response = MagicMock()
        mock_response.json.return_value = {"response": {"numFound": 0}}
        self.mock_session.get.return_value = mock_response

        result = recover_dependencies("org.fake:nonexistent", "1.0.0", "gradle", self.mock_session)

        assert result is None

    def test_recover_dependencies_version_sanitization(self):
        """Test that version strings are properly sanitized"""
        mock_response = MagicMock()
        self.mock_session.get.return_value = mock_response

        # Test with version containing special characters
        recover_dependencies("test-package", "^1.0.0-beta+build", "npm", self.mock_session)

        # Should sanitize version to only contain allowed characters
        expected_url = "https://deps.dev/_/s/npm/p/test-package/v/1.0.0-beta/dependencies"
        self.mock_session.get.assert_called_once_with(expected_url, timeout=10)

    def test_recover_dependencies_package_name_encoding(self):
        """Test that package names are properly URL encoded"""
        mock_response = MagicMock()
        self.mock_session.get.return_value = mock_response

        # Test with package name containing special characters
        recover_dependencies("@scope/package-name", "1.0.0", "npm", self.mock_session)

        # Should URL encode the package name
        expected_url = "https://deps.dev/_/s/npm/p/%40scope/package-name/v/1.0.0/dependencies"
        self.mock_session.get.assert_called_once_with(expected_url, timeout=10)

    @patch('utils.misc.sleep')
    @patch('builtins.print')
    def test_recover_dependencies_exception_handling(self, mock_print, mock_sleep):
        """Test recover_dependencies exception handling and rate limiting"""
        self.mock_session.get.side_effect = Exception("Network error")

        result = recover_dependencies("test-package", "1.0.0", "npm", self.mock_session)

        assert result is None
        mock_print.assert_called_once_with("[-] We have been rate limited, going to sleep for 5 minutes.")
        mock_sleep.assert_called_once_with(300)

    def test_caching_behavior(self):
        """Test that functions use caching decorator"""
        # The @cache decorator should ensure the same call returns cached result
        mock_response1 = MagicMock()
        mock_response1.status_code = 200
        mock_response2 = MagicMock()
        mock_response2.status_code = 404

        self.mock_session.get.side_effect = [mock_response1, mock_response2]

        # First call
        result1 = dependency_exists("test-package", "npm", self.mock_session)
        # Second call with same parameters should return cached result
        result2 = dependency_exists("test-package", "npm", self.mock_session)

        assert result1 == result2 == True
        # Should only make one actual HTTP request due to caching
        assert self.mock_session.get.call_count == 1