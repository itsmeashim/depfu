"""
NPM-specific tests for dependency recovery
"""
import pytest
import os
import tempfile
import shutil
import json
import sys

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from utils.recover_dependencies import RecoverDependencies


class TestNPMRecovery:
    """Test cases specific to NPM dependency recovery"""

    def setup_method(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()

    def teardown_method(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.temp_dir)

    def test_npm_complex_package_json(self):
        """Test complex NPM package.json with various dependency types"""
        package_json_content = {
            "name": "complex-npm-project",
            "version": "1.0.0",
            "dependencies": {
                "express": "^4.18.0",
                "lodash": "~4.17.21",
                "axios": "1.0.0",
                "git-dependency": "git+https://github.com/user/repo.git",
                "url-dependency": "https://registry.npmjs.org/package/-/package-1.0.0.tgz"
            },
            "devDependencies": {
                "jest": "^29.0.0",
                "eslint": ">=8.0.0"
            },
            "peerDependencies": {
                "react": "^18.0.0"
            },
            "optionalDependencies": {
                "fsevents": "^2.3.0"
            }
        }

        package_json_path = os.path.join(self.temp_dir, "package.json")
        with open(package_json_path, 'w') as f:
            json.dump(package_json_content, f)

        rd = RecoverDependencies(self.temp_dir, "npm")
        rd.get_npm_dependencies()

        # Should include regular dependencies but exclude git/url dependencies
        assert "express" in rd.dependencies
        assert "lodash" in rd.dependencies
        assert "axios" in rd.dependencies
        assert "jest" in rd.dependencies
        assert "eslint" in rd.dependencies

        # Should exclude git and URL dependencies
        assert "git-dependency" not in rd.dependencies
        assert "url-dependency" not in rd.dependencies

        # Note: peerDependencies and optionalDependencies are not processed by current implementation
        assert len(rd.dependencies) == 5

    def test_npm_nested_package_json(self):
        """Test NPM dependency recovery from nested package.json files"""
        # Create nested directory structure
        nested_dir = os.path.join(self.temp_dir, "subproject")
        os.makedirs(nested_dir)

        # Root package.json
        root_package = {
            "name": "root-project",
            "dependencies": {"express": "^4.18.0"}
        }
        with open(os.path.join(self.temp_dir, "package.json"), 'w') as f:
            json.dump(root_package, f)

        # Nested package.json
        nested_package = {
            "name": "nested-project",
            "dependencies": {"lodash": "^4.17.21"}
        }
        with open(os.path.join(nested_dir, "package.json"), 'w') as f:
            json.dump(nested_package, f)

        rd = RecoverDependencies(self.temp_dir, "npm")
        rd.get_npm_dependencies()

        # Should find dependencies from both files
        assert "express" in rd.dependencies
        assert "lodash" in rd.dependencies
        assert len(rd.dependencies) == 2