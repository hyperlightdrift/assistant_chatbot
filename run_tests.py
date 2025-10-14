#!/usr/bin/env python3
"""Test runner script for the assistant chatbot test suite."""

import subprocess
import sys
import os


def run_tests():
    """Run the test suite with appropriate configuration."""
    
    # Change to project directory
    project_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_dir)
    
    # Default pytest arguments
    pytest_args = [
        sys.executable, '-m', 'pytest',
        'tests/',
        '-v',
        '--tb=short',
        '--color=yes'
    ]
    
    # Add any command line arguments passed to this script
    if len(sys.argv) > 1:
        pytest_args.extend(sys.argv[1:])
    
    print(f"Running tests with command: {' '.join(pytest_args)}")
    print("=" * 60)
    
    try:
        result = subprocess.run(pytest_args, check=False)
        return result.returncode
    except KeyboardInterrupt:
        print("\nTests interrupted by user")
        return 1
    except Exception as e:
        print(f"Error running tests: {e}")
        return 1


if __name__ == '__main__':
    exit_code = run_tests()
    sys.exit(exit_code)
