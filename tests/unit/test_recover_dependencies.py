"""
Unit tests for RecoverDependencies class
"""
import pytest
import os
import tempfile
import shutil
import json
from unittest.mock import patch, mock_open
import sys

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from utils.recover_dependencies import RecoverDependencies


class TestRecoverDependencies:
    """Test cases for RecoverDependencies class"""

    def setup_method(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.rd = RecoverDependencies(self.temp_dir, "npm")

    def teardown_method(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.temp_dir)

    def test_init(self):
        """Test RecoverDependencies initialization"""
        rd = RecoverDependencies("/test/path", "npm")
        assert rd.path == "/test/path"
        assert rd.provider == "npm"
        assert rd.dependencies == {}
        assert rd.associate_projects_dependencies == {}
        assert rd.to_exclude == []

    def test_get_npm_dependencies(self):
        """Test NPM dependency extraction"""
        # Create a test package.json file
        package_json_content = {
            "name": "test-project",
            "dependencies": {
                "express": "^4.18.0",
                "lodash": "^4.17.21"
            },
            "devDependencies": {
                "jest": "^29.0.0"
            }
        }

        package_json_path = os.path.join(self.temp_dir, "package.json")
        with open(package_json_path, 'w') as f:
            json.dump(package_json_content, f)

        rd = RecoverDependencies(self.temp_dir, "npm")
        rd.get_npm_dependencies()

        expected_deps = {
            "express": "^4.18.0",
            "lodash": "^4.17.21",
            "jest": "^29.0.0"
        }
        assert rd.dependencies == expected_deps

    def test_get_npm_dependencies_with_workspaces(self):
        """Test NPM dependency extraction with workspaces exclusion"""
        package_json_content = {
            "name": "test-project",
            "workspaces": {
                "packages": ["packages/*"]
            },
            "dependencies": {
                "express": "^4.18.0",
                "workspace-package": "^1.0.0"
            }
        }

        package_json_path = os.path.join(self.temp_dir, "package.json")
        with open(package_json_path, 'w') as f:
            json.dump(package_json_content, f)

        rd = RecoverDependencies(self.temp_dir, "npm")
        rd.get_npm_dependencies()

        # Should include express but exclude workspace packages
        assert "express" in rd.dependencies
        assert rd.dependencies["express"] == "^4.18.0"

    def test_get_pypi_dependencies_requirements_txt(self):
        """Test Python dependency extraction from requirements.txt"""
        requirements_content = """requests==2.32.3
flask>=2.0.0
django==4.2.0
# This is a comment
numpy==1.24.0"""

        requirements_path = os.path.join(self.temp_dir, "requirements.txt")
        with open(requirements_path, 'w') as f:
            f.write(requirements_content)

        rd = RecoverDependencies(self.temp_dir, "pypi")
        rd.get_pypi_dependencies()

        expected_deps = {
            "requests": "2.32.3",
            "flask": "2.0.0",
            "django": "4.2.0",
            "numpy": "1.24.0"
        }
        assert rd.dependencies == expected_deps

    def test_get_cargo_dependencies(self):
        """Test Rust Cargo dependency extraction"""
        cargo_toml_content = """[package]
name = "test-rust-project"
version = "0.1.0"

[dependencies]
serde = "1.0"
tokio = { version = "1.0", features = ["full"] }
reqwest = "0.11"

[dev-dependencies]
tokio-test = "0.4"
"""

        cargo_toml_path = os.path.join(self.temp_dir, "Cargo.toml")
        with open(cargo_toml_path, 'w') as f:
            f.write(cargo_toml_content)

        rd = RecoverDependencies(self.temp_dir, "cargo")
        rd.get_cargo_dependencies()

        expected_deps = {
            "serde": "1.0",
            "tokio": "1.0",
            "reqwest": "0.11",
            "tokio-test": "0.4"
        }
        assert rd.dependencies == expected_deps

    def test_get_go_dependencies(self):
        """Test Go module dependency extraction"""
        go_mod_content = """module test-go-project

go 1.19

require (
    github.com/gin-gonic/gin v1.9.1
    github.com/stretchr/testify v1.8.4
)"""

        go_mod_path = os.path.join(self.temp_dir, "go.mod")
        with open(go_mod_path, 'w') as f:
            f.write(go_mod_content)

        rd = RecoverDependencies(self.temp_dir, "go")
        rd.get_go_dependencies()

        expected_deps = {
            "github.com/gin-gonic/gin": "v1.9.1",
            "github.com/stretchr/testify": "v1.8.4"
        }
        assert rd.dependencies == expected_deps