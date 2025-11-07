"""
Unit tests for EmailChecker class
"""
import pytest
import socket
from unittest.mock import patch, MagicMock
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from utils.email_checker import EmailChecker
from tests.fixtures.mock_responses import MOCK_NPM_REGISTRY_RESPONSE, MOCK_PYPI_RESPONSE


class TestEmailChecker:
    """Test cases for EmailChecker class"""

    def test_init(self):
        """Test EmailChecker initialization"""
        ec = EmailChecker("npm", "test-package")
        assert ec.provider == "npm"
        assert ec.package == "test-package"
        assert "npm" in ec.email_urls
        assert "pypi" in ec.email_urls
        assert "cargo" in ec.email_urls
        assert "gmail.com" in ec.known_domains

    @patch('requests.get')
    def test_get_emails_npm_success(self, mock_get):
        """Test email extraction from NPM registry"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = MOCK_NPM_REGISTRY_RESPONSE
        mock_get.return_value = mock_response

        ec = EmailChecker("npm", "test-package")
        emails = ec.get_emails()

        expected_emails = [
            "maintainer1@example.com",
            "maintainer2@testdomain.com",
            "contributor1@example.com"
        ]
        assert emails == expected_emails
        mock_get.assert_called_once_with("https://registry.npmjs.org/test-package", timeout=10)

    @patch('requests.get')
    def test_get_emails_pypi_success(self, mock_get):
        """Test email extraction from PyPI"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = MOCK_PYPI_RESPONSE
        mock_get.return_value = mock_response

        ec = EmailChecker("pypi", "test-package")
        emails = ec.get_emails()

        assert emails == ["author@testdomain.com"]
        mock_get.assert_called_once_with("https://pypi.org/pypi/test-package/json", timeout=10)

    @patch('requests.get')
    def test_get_emails_request_failure(self, mock_get):
        """Test email extraction when request fails"""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        ec = EmailChecker("npm", "test-package")
        emails = ec.get_emails()

        assert emails == []

    @patch('requests.get')
    def test_get_emails_request_exception(self, mock_get):
        """Test email extraction when request raises exception"""
        mock_get.side_effect = Exception("Network error")

        ec = EmailChecker("npm", "test-package")
        emails = ec.get_emails()

        assert emails == []

    def test_get_emails_unsupported_provider(self):
        """Test email extraction for unsupported providers"""
        ec = EmailChecker("go", "test-package")
        emails = ec.get_emails()

        assert emails == []

    def test_get_emails_cargo_provider(self):
        """Test email extraction for cargo provider (not supported)"""
        ec = EmailChecker("cargo", "test-package")
        emails = ec.get_emails()

        assert emails == []

    @patch('socket.gethostbyname')
    @patch('whois.whois')
    def test_check_email_domain_exists(self, mock_whois, mock_gethostbyname):
        """Test email checking when domain exists"""
        mock_gethostbyname.return_value = "192.168.1.1"  # Domain resolves

        ec = EmailChecker("npm", "test-package")

        with patch.object(ec, 'get_emails', return_value=["test@existingdomain.com"]):
            result = ec.check_email()

            assert result == []  # No takeoverable domains
            mock_gethostbyname.assert_called_once_with("existingdomain.com")

    @patch('socket.gethostbyname')
    @patch('whois.whois')
    def test_check_email_domain_not_registered(self, mock_whois, mock_gethostbyname):
        """Test email checking when domain is not registered"""
        mock_gethostbyname.side_effect = socket.error("Domain not found")
        mock_whois_result = {"registrar": None}
        mock_whois.return_value = mock_whois_result

        ec = EmailChecker("npm", "test-package")

        with patch.object(ec, 'get_emails', return_value=["test@takeoverable.com"]):
            result = ec.check_email()

            assert result == [["takeoverable.com", "test@takeoverable.com"]]
            mock_gethostbyname.assert_called_once_with("takeoverable.com")
            mock_whois.assert_called_once_with("takeoverable.com")

    @patch('socket.gethostbyname')
    @patch('whois.whois')
    def test_check_email_whois_exception(self, mock_whois, mock_gethostbyname):
        """Test email checking when whois raises exception"""
        mock_gethostbyname.side_effect = socket.error("Domain not found")
        mock_whois.side_effect = Exception("Whois error")

        ec = EmailChecker("npm", "test-package")

        with patch.object(ec, 'get_emails', return_value=["test@takeoverable.com"]):
            result = ec.check_email()

            assert result == [["takeoverable.com", "test@takeoverable.com"]]

    def test_check_email_known_domains_excluded(self):
        """Test that known domains are excluded from takeover check"""
        ec = EmailChecker("npm", "test-package")

        with patch.object(ec, 'get_emails', return_value=["test@gmail.com", "user@outlook.com"]):
            result = ec.check_email()

            assert result == []  # Known domains should be excluded

    def test_check_email_invalid_email_format(self):
        """Test email checking with invalid email formats"""
        ec = EmailChecker("npm", "test-package")

        with patch.object(ec, 'get_emails', return_value=["invalid-email", "not@an@email"]):
            result = ec.check_email()

            assert result == []  # Invalid emails should be filtered out

    def test_check_email_mixed_valid_invalid(self):
        """Test email checking with mix of valid and invalid emails"""
        ec = EmailChecker("npm", "test-package")

        with patch.object(ec, 'get_emails', return_value=["valid@test.com", "invalid-email", "another@gmail.com"]):
            with patch('socket.gethostbyname') as mock_gethostbyname:
                with patch('whois.whois') as mock_whois:
                    mock_gethostbyname.side_effect = socket.error("Domain not found")
                    mock_whois.return_value = {"registrar": None}

                    result = ec.check_email()

                    # Should only process valid@test.com (gmail.com is excluded)
                    assert result == [["test.com", "valid@test.com"]]