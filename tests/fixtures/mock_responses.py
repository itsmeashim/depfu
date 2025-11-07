"""
Mock API responses for testing
"""

# Mock response for existing package
MOCK_EXISTING_PACKAGE_RESPONSE = {
    "dependencyCount": 2,
    "dependencies": [
        {
            "package": {"name": "existing-package"},
            "version": "1.0.0"
        },
        {
            "package": {"name": "sub-dependency-1"},
            "version": "2.0.0"
        },
        {
            "package": {"name": "sub-dependency-2"},
            "version": "1.5.0"
        }
    ]
}

# Mock response for package with no dependencies
MOCK_NO_DEPS_RESPONSE = {
    "dependencyCount": 0,
    "dependencies": []
}

# Mock NPM registry response
MOCK_NPM_REGISTRY_RESPONSE = {
    "name": "test-package",
    "version": "1.0.0",
    "maintainers": [
        {"name": "maintainer1", "email": "maintainer1@example.com"},
        {"name": "maintainer2", "email": "maintainer2@testdomain.com"}
    ],
    "contributors": [
        {"name": "contributor1", "email": "contributor1@example.com"}
    ]
}

# Mock PyPI response
MOCK_PYPI_RESPONSE = {
    "info": {
        "name": "test-package",
        "version": "1.0.0",
        "author_email": "author@testdomain.com"
    }
}

# Mock Maven search response
MOCK_MAVEN_SEARCH_RESPONSE = {
    "response": {
        "numFound": 1,
        "docs": [
            {
                "id": "org.example:test-artifact:1.0.0",
                "g": "org.example",
                "a": "test-artifact",
                "v": "1.0.0"
            }
        ]
    }
}