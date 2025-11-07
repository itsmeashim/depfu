"""
Test-specific configuration and fixtures
"""
import pytest
import os
import json
import tempfile
import shutil


@pytest.fixture
def sample_package_json():
    """Sample package.json content for testing"""
    return {
        "name": "test-project",
        "version": "1.0.0",
        "dependencies": {
            "express": "^4.18.0",
            "lodash": "^4.17.21",
            "fake-package": "^1.0.0"
        },
        "devDependencies": {
            "jest": "^29.0.0",
            "fake-dev-package": "^2.0.0"
        }
    }


@pytest.fixture
def sample_requirements_txt():
    """Sample requirements.txt content for testing"""
    return """requests==2.32.3
flask>=2.0.0
fake-python-package==1.0.0
pytest>=7.0.0"""


@pytest.fixture
def sample_cargo_toml():
    """Sample Cargo.toml content for testing"""
    return """[package]
name = "test-rust-project"
version = "0.1.0"

[dependencies]
serde = "1.0"
tokio = "1.0"
fake-rust-crate = "1.0.0"

[dev-dependencies]
tokio-test = "0.4"
"""


@pytest.fixture
def create_test_project(temp_directory):
    """Create a test project with multiple package managers"""
    def _create_project(providers=None):
        if providers is None:
            providers = ["npm"]

        project_files = {}

        if "npm" in providers:
            package_json = {
                "name": "test-project",
                "dependencies": {"express": "^4.18.0", "fake-npm-pkg": "^1.0.0"}
            }
            package_json_path = os.path.join(temp_directory, "package.json")
            with open(package_json_path, 'w') as f:
                json.dump(package_json, f)
            project_files["package.json"] = package_json_path

        if "pypi" in providers:
            requirements_content = "requests==2.32.3\nfake-python-pkg==1.0.0"
            requirements_path = os.path.join(temp_directory, "requirements.txt")
            with open(requirements_path, 'w') as f:
                f.write(requirements_content)
            project_files["requirements.txt"] = requirements_path

        return project_files

    return _create_project