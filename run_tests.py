#!/usr/bin/env python3
"""
Test runner script for DepFuzzer
"""
import sys
import subprocess
import argparse
from pathlib import Path


def run_command(cmd, description):
    """Run a command and handle errors"""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(cmd)}")
    print(f"{'='*60}")

    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        return True
    except subprocess.CalledProcessError as e:
        print(f"ERROR: {description} failed!")
        print(f"Return code: {e.returncode}")
        print(f"STDOUT: {e.stdout}")
        print(f"STDERR: {e.stderr}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Run DepFuzzer tests")
    parser.add_argument("--unit", action="store_true", help="Run only unit tests")
    parser.add_argument("--integration", action="store_true", help="Run only integration tests")
    parser.add_argument("--provider", choices=["npm", "pypi", "cargo", "go", "maven", "gradle", "rubygems"],
                       help="Run tests for specific provider")
    parser.add_argument("--coverage", action="store_true", help="Run with coverage report")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--fast", action="store_true", help="Skip slow tests")

    args = parser.parse_args()

    # Base pytest command
    cmd = ["python", "-m", "pytest"]

    # Add verbosity
    if args.verbose:
        cmd.append("-vv")

    # Add coverage if requested
    if args.coverage:
        cmd.extend(["--cov=utils", "--cov=main", "--cov-report=html", "--cov-report=term"])

    # Add test selection
    if args.unit:
        cmd.append("-m unit")
    elif args.integration:
        cmd.append("-m integration")
    elif args.provider:
        cmd.append(f"-m {args.provider}")

    # Skip slow tests if requested
    if args.fast:
        cmd.append("-m 'not slow'")

    # Add test directory
    cmd.append("tests/")

    # Check if pytest is available
    try:
        subprocess.run(["python", "-m", "pytest", "--version"], check=True, capture_output=True)
    except subprocess.CalledProcessError:
        print("ERROR: pytest is not installed!")
        print("Please install it with: pip install pytest")
        if args.coverage:
            print("For coverage support, also install: pip install pytest-cov")
        return 1

    # Run the tests
    success = run_command(cmd, "Running tests")

    if success:
        print(f"\n{'='*60}")
        print("✅ All tests passed!")
        print(f"{'='*60}")
        return 0
    else:
        print(f"\n{'='*60}")
        print("❌ Some tests failed!")
        print(f"{'='*60}")
        return 1


if __name__ == "__main__":
    sys.exit(main())