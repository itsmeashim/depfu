"""
Unit tests for AnalyzeDependencies class
"""
import pytest
import tempfile
import os
from unittest.mock import patch, MagicMock, mock_open
import sys

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from utils.analyze_dependencies import AnalyzeDependencies
from tests.fixtures.mock_responses import MOCK_EXISTING_PACKAGE_RESPONSE, MOCK_NO_DEPS_RESPONSE


class TestAnalyzeDependencies:
    """Test cases for AnalyzeDependencies class"""

    def setup_method(self):
        """Set up test fixtures"""
        self.dependencies = {"test-package": "1.0.0", "another-package": "2.0.0"}
        self.analyzer = AnalyzeDependencies(
            provider="npm",
            dependencies=self.dependencies,
            print_takeover=False,
            output=None,
            check_email=False
        )

    def test_init(self):
        """Test AnalyzeDependencies initialization"""
        analyzer = AnalyzeDependencies("pypi", {"pkg": "1.0"}, True, "output.txt", True)
        assert analyzer.provider == "pypi"
        assert analyzer.dependencies == {"pkg": "1.0"}
        assert analyzer.print_takeover is True
        assert analyzer.output == "output.txt"
        assert analyzer.check is True
        assert analyzer.takeover == {}
        assert analyzer.already_done == {}
        assert analyzer.email_takeover == []

    @patch('utils.analyze_dependencies.dependency_exists')
    @patch('utils.analyze_dependencies.recover_dependencies')
    def test_check_dependency_existing_package(self, mock_recover, mock_exists):
        """Test checking an existing dependency"""
        mock_exists.return_value = True
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = MOCK_EXISTING_PACKAGE_RESPONSE
        mock_recover.return_value = mock_response

        self.analyzer.check_dependency("test-package", "1.0.0")

        mock_exists.assert_called_with("test-package", "npm", self.analyzer.session)
        mock_recover.assert_called_with("test-package", "1.0.0", "npm", self.analyzer.session)
        assert "test-package" in self.analyzer.already_done
        assert "test-package" not in self.analyzer.takeover

    @patch('utils.analyze_dependencies.dependency_exists')
    def test_check_dependency_nonexistent_package(self, mock_exists):
        """Test checking a non-existent dependency"""
        mock_exists.return_value = False

        self.analyzer.check_dependency("fake-package", "1.0.0")

        mock_exists.assert_called_with("fake-package", "npm", self.analyzer.session)
        assert "fake-package" in self.analyzer.already_done
        assert "fake-package" in self.analyzer.takeover
        assert self.analyzer.takeover["fake-package"] == "1.0.0"

    @patch('utils.analyze_dependencies.dependency_exists')
    @patch('utils.analyze_dependencies.recover_dependencies')
    def test_check_dependency_with_subdependencies(self, mock_recover, mock_exists):
        """Test checking dependency that has sub-dependencies"""
        mock_exists.side_effect = lambda pkg, provider, session: pkg in ["test-package", "sub-dependency-1"]

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = MOCK_EXISTING_PACKAGE_RESPONSE
        mock_recover.return_value = mock_response

        self.analyzer.check_dependency("test-package", "1.0.0")

        # Should check the main package and its sub-dependencies
        assert mock_exists.call_count >= 2
        assert "test-package" in self.analyzer.already_done
        assert "sub-dependency-1" in self.analyzer.already_done

    def test_analyze_dependencies(self):
        """Test analyzing all dependencies"""
        with patch.object(self.analyzer, 'check_dependency') as mock_check:
            self.analyzer.analyze_dependencies()

            # Should call check_dependency for each dependency
            assert mock_check.call_count == 2
            mock_check.assert_any_call("test-package", "1.0.0")
            mock_check.assert_any_call("another-package", "2.0.0")

    @patch('utils.analyze_dependencies.EmailChecker')
    def test_check_email(self, mock_email_checker):
        """Test email checking functionality"""
        mock_ec_instance = MagicMock()
        mock_ec_instance.check_email.return_value = [("testdomain.com", "test@testdomain.com")]
        mock_email_checker.return_value = mock_ec_instance

        analyzer = AnalyzeDependencies("npm", {}, False, None, True)

        with patch('builtins.print') as mock_print:
            analyzer.check_email("test-package")

            mock_email_checker.assert_called_with("npm", "test-package")
            mock_ec_instance.check_email.assert_called_once()
            assert "testdomain.com" in analyzer.email_takeover
            mock_print.assert_called_once()

    def test_run_with_takeover_packages_no_output(self):
        """Test run method with takeover packages but no output file"""
        self.analyzer.takeover = {"fake-package": "1.0.0", "another-fake": "2.0.0"}

        with patch.object(self.analyzer, 'analyze_dependencies'):
            with patch('builtins.print') as mock_print:
                self.analyzer.run()

                # Should print takeover packages
                mock_print.assert_any_call("[+] fake-package:1.0.0 might be taken over !")
                mock_print.assert_any_call("[+] another-fake:2.0.0 might be taken over !")

    def test_run_with_takeover_packages_with_output(self):
        """Test run method with takeover packages and output file"""
        self.analyzer.takeover = {"fake-package": "1.0.0"}
        self.analyzer.output = "test_output.txt"

        with patch.object(self.analyzer, 'analyze_dependencies'):
            with patch('builtins.open', mock_open()) as mock_file:
                with patch('builtins.print') as mock_print:
                    self.analyzer.run()

                    mock_file.assert_called_once_with("test_output.txt", "w", encoding="utf-8")
                    mock_file().write.assert_called_with("fake-package:1.0.0\n")
                    mock_print.assert_any_call("Results saved to test_output.txt !")

    def test_run_no_takeover_packages(self):
        """Test run method when no packages can be taken over"""
        self.analyzer.takeover = {}

        with patch.object(self.analyzer, 'analyze_dependencies'):
            with patch('builtins.print') as mock_print:
                self.analyzer.run()

                mock_print.assert_any_call("[+] No package can be taken over !")

    def test_scoped_package_handling(self):
        """Test handling of scoped packages (with @)"""
        with patch('utils.analyze_dependencies.dependency_exists') as mock_exists:
            mock_exists.return_value = False

            with patch('builtins.print') as mock_print:
                analyzer = AnalyzeDependencies("npm", {}, True, None, False)
                analyzer.check_dependency("@scope/package", "1.0.0")

                # Should recognize scoped package and print appropriate message
                mock_print.assert_called_with(
                    "[DEBUG] @scope/package is not declared but cannot be taken over because it belongs to an external organization\nYou might have to check manually if the organization exists."
                )