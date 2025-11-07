# DepFuzzer Testing Guide

## Overview

A comprehensive test suite has been created for the DepFuzzer dependency analysis tool. The test suite includes unit tests, integration tests, and provider-specific tests with a nested folder structure.

## Quick Start

1. **Install testing dependencies:**
   ```bash
   pip install -r requirements-test.txt
   ```

2. **Run all tests:**
   ```bash
   python3 run_tests.py
   ```

3. **Run with coverage:**
   ```bash
   python3 run_tests.py --coverage
   ```

## Test Structure

The test suite is organized with the following structure:

```
tests/
├── unit/                       # Unit tests for individual components
├── integration/                # End-to-end integration tests
├── providers/                  # Provider-specific tests (nested structure)
│   ├── npm/
│   ├── pypi/
│   ├── cargo/
│   ├── go/
│   ├── maven/
│   ├── gradle/
│   └── rubygems/
└── fixtures/                   # Test data and mock responses
```

## Test Coverage

### Unit Tests
- **main.py**: Argument parsing, main function logic, provider selection
- **RecoverDependencies**: Dependency extraction for all 7 supported providers
- **AnalyzeDependencies**: Dependency analysis, takeover detection, output generation
- **EmailChecker**: Email extraction and domain validation
- **misc.py**: API utilities with proper mocking

### Integration Tests
- End-to-end workflows combining dependency recovery and analysis
- Multi-provider project structures
- Output file generation
- Email checking integration

### Provider-Specific Tests
- **NPM**: Complex package.json parsing, workspaces, nested projects
- **PyPI**: requirements.txt and pyproject.toml parsing, Poetry support
- **Cargo**: Cargo.toml parsing with dev-dependencies and patches
- **Go**: go.mod parsing with require blocks
- **Maven**: pom.xml parsing with XML structure
- **Gradle**: build.gradle parsing with Groovy syntax
- **RubyGems**: Gemfile parsing with groups

## Running Tests

### Using the Test Runner (Recommended)

```bash
# Run all tests
python3 run_tests.py

# Run specific test types
python3 run_tests.py --unit
python3 run_tests.py --integration

# Run provider-specific tests
python3 run_tests.py --provider npm
python3 run_tests.py --provider pypi

# Run with coverage and verbose output
python3 run_tests.py --coverage --verbose

# Skip slow tests for faster feedback
python3 run_tests.py --fast
```

### Using pytest directly

```bash
# Run all tests
pytest

# Run with markers
pytest -m unit
pytest -m integration
pytest -m npm

# Run specific files
pytest tests/unit/test_main.py
pytest tests/providers/npm/
```

## Key Features

1. **Comprehensive Mocking**: All external API calls are mocked for deterministic tests
2. **Realistic Test Data**: Sample project files for all supported package managers
3. **Error Handling**: Tests cover exception scenarios and edge cases
4. **Nested Structure**: Provider-specific tests are organized in nested folders
5. **Flexible Runner**: Custom test runner with multiple options
6. **CI/CD Ready**: Configured for continuous integration systems

## Test Files Created

### Core Test Files
- `tests/unit/test_main.py` - Main script functionality
- `tests/unit/test_recover_dependencies.py` - Dependency recovery
- `tests/unit/test_analyze_dependencies.py` - Dependency analysis
- `tests/unit/test_email_checker.py` - Email validation
- `tests/unit/test_misc.py` - Utility functions
- `tests/integration/test_end_to_end.py` - Integration workflows

### Provider-Specific Tests
- `tests/providers/npm/test_npm_recovery.py` - NPM-specific tests
- `tests/providers/pypi/test_pypi_recovery.py` - PyPI-specific tests
- Additional provider folders ready for expansion

### Configuration and Fixtures
- `pytest.ini` - Pytest configuration
- `conftest.py` - Global fixtures and configuration
- `tests/conftest.py` - Test-specific fixtures
- `tests/fixtures/mock_responses.py` - Mock API responses
- Sample project files for all providers
- `run_tests.py` - Custom test runner
- `requirements-test.txt` - Testing dependencies

## Next Steps

1. **Install dependencies**: `pip install -r requirements-test.txt`
2. **Run tests**: `python3 run_tests.py --coverage`
3. **Add more provider tests**: Expand tests in provider-specific folders
4. **Set up CI/CD**: Use the provided configuration for automated testing

The test suite provides comprehensive coverage of the DepFuzzer functionality and is ready for immediate use!