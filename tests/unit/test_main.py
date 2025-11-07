"""
Unit tests for main.py
"""
import pytest
import argparse
from unittest.mock import patch, MagicMock
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from main import main


class TestMain:
    """Test cases for main.py functionality"""

    def test_argument_parser_with_path_and_provider(self):
        """Test argument parser with path and provider arguments"""
        with patch('sys.argv', ['main.py', '--provider', 'npm', '--path', '/test/path']):
            with patch('main.RecoverDependencies') as mock_rd:
                with patch('main.AnalyzeDependencies') as mock_ad:
                    mock_rd_instance = MagicMock()
                    mock_rd_instance.dependencies = {'test-package': '1.0.0'}
                    mock_rd.return_value = mock_rd_instance

                    mock_ad_instance = MagicMock()
                    mock_ad.return_value = mock_ad_instance

                    with patch('main.Figlet') as mock_figlet:
                        mock_figlet_instance = MagicMock()
                        mock_figlet_instance.renderText.return_value = "DepFuzzer"
                        mock_figlet.return_value = mock_figlet_instance

                        main()

                        mock_rd.assert_called_once_with('/test/path', 'npm')
                        mock_rd_instance.run.assert_called_once()
                        mock_ad.assert_called_once_with('npm', {'test-package': '1.0.0'}, False, None, False)
                        mock_ad_instance.run.assert_called_once()

    def test_argument_parser_with_dependency_and_version(self):
        """Test argument parser with dependency name and version"""
        with patch('sys.argv', ['main.py', '--provider', 'pypi', '--dependency', 'requests:2.25.0']):
            with patch('main.AnalyzeDependencies') as mock_ad:
                mock_ad_instance = MagicMock()
                mock_ad.return_value = mock_ad_instance

                with patch('main.Figlet') as mock_figlet:
                    mock_figlet_instance = MagicMock()
                    mock_figlet_instance.renderText.return_value = "DepFuzzer"
                    mock_figlet.return_value = mock_figlet_instance

                    main()

                    mock_ad.assert_called_once_with('pypi', {'requests': '2.25.0'}, False, None, False)
                    mock_ad_instance.run.assert_called_once()

    def test_argument_parser_with_dependency_no_version(self):
        """Test argument parser with dependency name but no version"""
        with patch('sys.argv', ['main.py', '--provider', 'cargo', '--dependency', 'serde']):
            with patch('main.AnalyzeDependencies') as mock_ad:
                mock_ad_instance = MagicMock()
                mock_ad.return_value = mock_ad_instance

                with patch('main.Figlet') as mock_figlet:
                    mock_figlet_instance = MagicMock()
                    mock_figlet_instance.renderText.return_value = "DepFuzzer"
                    mock_figlet.return_value = mock_figlet_instance

                    main()

                    mock_ad.assert_called_once_with('cargo', {'serde': ''}, False, None, False)
                    mock_ad_instance.run.assert_called_once()

    def test_all_providers_option(self):
        """Test the 'all' provider option"""
        with patch('sys.argv', ['main.py', '--provider', 'all', '--path', '/test/path']):
            with patch('main.RecoverDependencies') as mock_rd:
                with patch('main.AnalyzeDependencies') as mock_ad:
                    # Mock different dependencies for different providers
                    mock_rd_instances = []
                    for provider in ["npm", "pypi", "cargo", "go", "maven", "gradle", "rubygems"]:
                        mock_instance = MagicMock()
                        mock_instance.dependencies = {f'{provider}-package': '1.0.0'}
                        mock_rd_instances.append(mock_instance)

                    mock_rd.side_effect = mock_rd_instances

                    mock_ad_instance = MagicMock()
                    mock_ad.return_value = mock_ad_instance

                    with patch('main.Figlet') as mock_figlet:
                        mock_figlet_instance = MagicMock()
                        mock_figlet_instance.renderText.return_value = "DepFuzzer"
                        mock_figlet.return_value = mock_figlet_instance

                        main()

                        # Should be called 7 times (once for each provider)
                        assert mock_rd.call_count == 7
                        assert mock_ad.call_count == 7

    def test_no_dependencies_found(self):
        """Test behavior when no dependencies are found"""
        with patch('sys.argv', ['main.py', '--provider', 'npm', '--path', '/test/path']):
            with patch('main.RecoverDependencies') as mock_rd:
                mock_rd_instance = MagicMock()
                mock_rd_instance.dependencies = {}  # No dependencies
                mock_rd.return_value = mock_rd_instance

                with patch('main.Figlet') as mock_figlet:
                    mock_figlet_instance = MagicMock()
                    mock_figlet_instance.renderText.return_value = "DepFuzzer"
                    mock_figlet.return_value = mock_figlet_instance

                    with patch('builtins.print') as mock_print:
                        main()

                        mock_print.assert_any_call("[-] No package for npm found.")

    def test_optional_arguments(self):
        """Test optional arguments like print-takeover, output-file, check-email"""
        with patch('sys.argv', ['main.py', '--provider', 'npm', '--dependency', 'test-pkg',
                                '--print-takeover', 'True', '--output-file', 'output.txt',
                                '--check-email', 'True']):
            with patch('main.AnalyzeDependencies') as mock_ad:
                mock_ad_instance = MagicMock()
                mock_ad.return_value = mock_ad_instance

                with patch('main.Figlet') as mock_figlet:
                    mock_figlet_instance = MagicMock()
                    mock_figlet_instance.renderText.return_value = "DepFuzzer"
                    mock_figlet.return_value = mock_figlet_instance

                    main()

                    mock_ad.assert_called_once_with('npm', {'test-pkg': ''}, True, 'output.txt', True)
                    mock_ad_instance.run.assert_called_once()