"""
Integration tests for end-to-end workflows
"""
import pytest
import tempfile
import shutil
import os
import json
from unittest.mock import patch, MagicMock
import sys

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from utils.recover_dependencies import RecoverDependencies
from utils.analyze_dependencies import AnalyzeDependencies


class TestEndToEndWorkflows:
    """Integration tests for complete workflows"""

    def setup_method(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()

    def teardown_method(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.temp_dir)

    def create_sample_npm_project(self):
        """Create a sample NPM project structure"""
        package_json = {
            "name": "test-npm-project",
            "version": "1.0.0",
            "dependencies": {
                "express": "^4.18.0",
                "lodash": "^4.17.21",
                "fake-npm-package": "^1.0.0"
            },
            "devDependencies": {
                "jest": "^29.0.0",
                "fake-dev-package": "^2.0.0"
            }
        }

        with open(os.path.join(self.temp_dir, "package.json"), 'w') as f:
            json.dump(package_json, f)

    def create_sample_python_project(self):
        """Create a sample Python project structure"""
        requirements_content = """requests==2.32.3
flask>=2.0.0
fake-python-package==1.0.0
pytest>=7.0.0"""

        with open(os.path.join(self.temp_dir, "requirements.txt"), 'w') as f:
            f.write(requirements_content)

    @patch('utils.misc.dependency_exists')
    @patch('utils.misc.recover_dependencies')
    def test_npm_end_to_end_workflow(self, mock_recover, mock_exists):
        """Test complete NPM analysis workflow"""
        self.create_sample_npm_project()

        # Mock API responses
        def mock_exists_side_effect(package, provider, session):
            # Simulate that express and lodash exist, but fake packages don't
            return package in ["express", "lodash", "jest"]

        mock_exists.side_effect = mock_exists_side_effect

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"dependencyCount": 0, "dependencies": []}
        mock_recover.return_value = mock_response

        # Step 1: Recover dependencies
        rd = RecoverDependencies(self.temp_dir, "npm")
        rd.run()

        # Verify dependencies were found
        assert len(rd.dependencies) == 5
        assert "express" in rd.dependencies
        assert "fake-npm-package" in rd.dependencies

        # Step 2: Analyze dependencies
        analyzer = AnalyzeDependencies("npm", rd.dependencies, False, None, False)
        analyzer.run()

        # Verify takeover packages were identified
        assert "fake-npm-package" in analyzer.takeover
        assert "fake-dev-package" in analyzer.takeover
        assert "express" not in analyzer.takeover  # Should exist
        assert "lodash" not in analyzer.takeover   # Should exist

    @patch('utils.misc.dependency_exists')
    @patch('utils.misc.recover_dependencies')
    def test_python_end_to_end_workflow(self, mock_recover, mock_exists):
        """Test complete Python analysis workflow"""
        self.create_sample_python_project()

        # Mock API responses
        def mock_exists_side_effect(package, provider, session):
            # Simulate that requests and flask exist, but fake package doesn't
            return package in ["requests", "flask", "pytest"]

        mock_exists.side_effect = mock_exists_side_effect

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"dependencyCount": 0, "dependencies": []}
        mock_recover.return_value = mock_response

        # Step 1: Recover dependencies
        rd = RecoverDependencies(self.temp_dir, "pypi")
        rd.run()

        # Verify dependencies were found
        assert len(rd.dependencies) == 4
        assert "requests" in rd.dependencies
        assert "fake-python-package" in rd.dependencies

        # Step 2: Analyze dependencies
        analyzer = AnalyzeDependencies("pypi", rd.dependencies, False, None, False)
        analyzer.run()

        # Verify takeover packages were identified
        assert "fake-python-package" in analyzer.takeover
        assert "requests" not in analyzer.takeover  # Should exist

    def test_multi_provider_project_structure(self):
        """Test project with multiple package managers"""
        # Create a project with both NPM and Python dependencies
        self.create_sample_npm_project()
        self.create_sample_python_project()

        # Test NPM recovery
        rd_npm = RecoverDependencies(self.temp_dir, "npm")
        rd_npm.run()
        assert len(rd_npm.dependencies) > 0
        assert "express" in rd_npm.dependencies

        # Test Python recovery
        rd_python = RecoverDependencies(self.temp_dir, "pypi")
        rd_python.run()
        assert len(rd_python.dependencies) > 0
        assert "requests" in rd_python.dependencies

    @patch('utils.misc.dependency_exists')
    @patch('utils.misc.recover_dependencies')
    def test_output_file_generation(self, mock_recover, mock_exists):
        """Test output file generation for takeover packages"""
        self.create_sample_npm_project()

        # Mock all packages as non-existent for takeover
        mock_exists.return_value = False
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"dependencyCount": 0, "dependencies": []}
        mock_recover.return_value = mock_response

        output_file = os.path.join(self.temp_dir, "takeover_results.txt")

        # Recover and analyze dependencies
        rd = RecoverDependencies(self.temp_dir, "npm")
        rd.run()

        analyzer = AnalyzeDependencies("npm", rd.dependencies, False, output_file, False)
        analyzer.run()

        # Verify output file was created
        assert os.path.exists(output_file)

        # Verify output file contains expected packages
        with open(output_file, 'r') as f:
            content = f.read()
            assert "express:" in content
            assert "fake-npm-package:" in content

    @patch('utils.misc.dependency_exists')
    @patch('utils.misc.recover_dependencies')
    @patch('utils.analyze_dependencies.EmailChecker')
    def test_email_checking_integration(self, mock_email_checker, mock_recover, mock_exists):
        """Test integration with email checking functionality"""
        self.create_sample_npm_project()

        # Mock dependencies as non-existent
        mock_exists.return_value = False
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"dependencyCount": 0, "dependencies": []}
        mock_recover.return_value = mock_response

        # Mock email checker
        mock_ec_instance = MagicMock()
        mock_ec_instance.check_email.return_value = [("takeoverable.com", "test@takeoverable.com")]
        mock_email_checker.return_value = mock_ec_instance

        # Recover and analyze dependencies with email checking enabled
        rd = RecoverDependencies(self.temp_dir, "npm")
        rd.run()

        analyzer = AnalyzeDependencies("npm", rd.dependencies, False, None, True)

        with patch('builtins.print') as mock_print:
            analyzer.run()

            # Verify email checker was called for each package
            assert mock_email_checker.call_count == len(rd.dependencies)

            # Verify email takeover message was printed
            mock_print.assert_any_call(
                "The account associated to dependency express is : test@takeoverable.com and the domain takeoverable.com might be purchased !"
            )