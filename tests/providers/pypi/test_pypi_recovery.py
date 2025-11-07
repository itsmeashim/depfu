"""
PyPI-specific tests for dependency recovery
"""
import pytest
import os
import tempfile
import shutil
import sys

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from utils.recover_dependencies import RecoverDependencies


class TestPyPIRecovery:
    """Test cases specific to PyPI dependency recovery"""

    def setup_method(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()

    def teardown_method(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.temp_dir)

    def test_pyproject_toml_project_dependencies(self):
        """Test pyproject.toml with project dependencies"""
        pyproject_content = """[project]
name = "test-python-project"
version = "0.1.0"
dependencies = [
    "requests>=2.25.0",
    "click>=8.0.0",
    "numpy==1.24.0"
]
"""

        pyproject_path = os.path.join(self.temp_dir, "pyproject.toml")
        with open(pyproject_path, 'w') as f:
            f.write(pyproject_content)

        rd = RecoverDependencies(self.temp_dir, "pypi")
        rd.get_pypi_dependencies()

        assert "requests" in rd.dependencies
        assert "click" in rd.dependencies
        assert "numpy" in rd.dependencies
        assert rd.dependencies["numpy"] == "1.24.0"

    def test_poetry_dependencies(self):
        """Test pyproject.toml with Poetry dependencies"""
        pyproject_content = """[tool.poetry]
name = "test-poetry-project"
version = "0.1.0"

[tool.poetry.dependencies]
python = "^3.8"
fastapi = "^0.68.0"
uvicorn = "^0.15.0"

[tool.poetry.dev-dependencies]
pytest = "^6.2.0"
black = "^21.0.0"
"""

        pyproject_path = os.path.join(self.temp_dir, "pyproject.toml")
        with open(pyproject_path, 'w') as f:
            f.write(pyproject_content)

        rd = RecoverDependencies(self.temp_dir, "pypi")
        rd.get_pypi_dependencies()

        # Should extract package names from poetry dependencies
        assert "fastapi" in rd.dependencies
        assert "uvicorn" in rd.dependencies
        assert "pytest" in rd.dependencies
        assert "black" in rd.dependencies

    def test_requirements_txt_variations(self):
        """Test various requirements.txt file formats"""
        requirements_content = """# Production dependencies
requests==2.32.3
flask>=2.0.0,<3.0.0
django~=4.2.0

# Development dependencies
pytest>=7.0.0
black

# With extras
requests[security]==2.32.3

# With comments inline
numpy==1.24.0  # Scientific computing

# Git dependencies (should be ignored by current implementation)
git+https://github.com/user/repo.git@v1.0.0#egg=package-name

# Editable installs
-e git+https://github.com/user/repo.git#egg=editable-package
"""

        requirements_path = os.path.join(self.temp_dir, "requirements.txt")
        with open(requirements_path, 'w') as f:
            f.write(requirements_content)

        rd = RecoverDependencies(self.temp_dir, "pypi")
        rd.get_pypi_dependencies()

        # Should parse standard requirements
        assert "requests" in rd.dependencies
        assert "flask" in rd.dependencies
        assert "django" in rd.dependencies
        assert "pytest" in rd.dependencies
        assert "black" in rd.dependencies
        assert "numpy" in rd.dependencies