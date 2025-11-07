# DepFuzzer Test Suite

This directory contains comprehensive tests for the DepFuzzer dependency analysis tool.

## Test Structure

```
tests/
├── __init__.py
├── conftest.py                 # Test configuration and fixtures
├── README.md                   # This file
├── fixtures/                   # Test data and mock responses
│   ├── __init__.py
│   ├── mock_responses.py       # Mock API responses
│   ├── sample_package.json     # Sample NPM package file
│   ├── sample_requirements.txt # Sample Python requirements
│   ├── sample_pyproject.toml   # Sample Python project file
│   ├── sample_Cargo.toml       # Sample Rust Cargo file
│   ├── sample_go.mod           # Sample Go module file
│   ├── sample_pom.xml          # Sample Maven POM file
│   ├── sample_build.gradle     # Sample Gradle build file
│   └── sample_Gemfile          # Sample Ruby Gemfile
├── unit/                       # Unit tests
│   ├── __init__.py
│   ├── test_main.py           # Tests for main.py
│   ├── test_recover_dependencies.py  # Tests for RecoverDependencies
│   ├── test_analyze_dependencies.py  # Tests for AnalyzeDependencies
│   ├── test_email_checker.py  # Tests for EmailChecker
│   └── test_misc.py           # Tests for misc utilities
├── integration/                # Integration tests
│   ├── __init__.py
│   └── test_end_to_end.py     # End-to-end workflow tests
└── providers/                  # Provider-specific tests
    ├── __init__.py
    ├── npm/
    │   ├── __init__.py
    │   └── test_npm_recovery.py
    ├── pypi/
    │   ├── __init__.py
    │   └── test_pypi_recovery.py
    ├── cargo/
    │   └── __init__.py
    ├── go/
    │   └── __init__.py
    ├── maven/
    │   └── __init__.py
    ├── gradle/
    │   └── __init__.py
    └── rubygems/
        └── __init__.py
```

## Running Tests

### Prerequisites

Install the required testing dependencies:

```bash
pip install pytest pytest-cov
```

### Using the Test Runner

The easiest way to run tests is using the provided test runner:

```bash
# Run all tests
python run_tests.py

# Run only unit tests
python run_tests.py --unit

# Run only integration tests
python run_tests.py --integration

# Run tests for a specific provider
python run_tests.py --provider npm

# Run with coverage report
python run_tests.py --coverage

# Run with verbose output
python run_tests.py --verbose

# Skip slow tests
python run_tests.py --fast
```

### Using pytest directly

You can also run pytest directly:

```bash
# Run all tests
pytest

# Run specific test categories
pytest -m unit
pytest -m integration
pytest -m npm

# Run specific test files
pytest tests/unit/test_main.py
pytest tests/providers/npm/

# Run with coverage
pytest --cov=utils --cov=main --cov-report=html

# Run with verbose output
pytest -v
```

## Test Categories

Tests are organized using pytest markers:

- `unit`: Unit tests for individual components
- `integration`: End-to-end integration tests
- `npm`: NPM provider-specific tests
- `pypi`: PyPI provider-specific tests
- `cargo`: Cargo provider-specific tests
- `go`: Go provider-specific tests
- `maven`: Maven provider-specific tests
- `gradle`: Gradle provider-specific tests
- `rubygems`: RubyGems provider-specific tests
- `slow`: Tests that take longer to run
- `network`: Tests that require network access

## Test Coverage

The test suite covers:

1. **Argument parsing and main function logic**
2. **Dependency recovery for all supported providers**
3. **Dependency analysis and takeover detection**
4. **Email checking and domain validation**
5. **API interaction utilities**
6. **End-to-end workflows**
7. **Error handling and edge cases**

## Writing New Tests

When adding new tests:

1. Place unit tests in `tests/unit/`
2. Place integration tests in `tests/integration/`
3. Place provider-specific tests in `tests/providers/{provider}/`
4. Use appropriate pytest markers
5. Follow the existing naming conventions
6. Add fixtures to `conftest.py` if they're reusable
7. Mock external API calls to ensure tests are deterministic

## Continuous Integration

The test suite is designed to work with CI/CD systems. Example GitHub Actions workflow:

```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.8, 3.9, '3.10', 3.11]
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-cov
    - name: Run tests
      run: python run_tests.py --coverage
```