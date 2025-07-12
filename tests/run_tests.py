#!/usr/bin/env python3
"""
Test runner for propER system
Runs all tests in the tests directory
"""

import os
import sys
import unittest

# Add the parent directory to the path so we can import app modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def run_tests():
    """Discover and run all tests"""
    # Discover tests in the current directory
    loader = unittest.TestLoader()
    start_dir = os.path.dirname(os.path.abspath(__file__))
    suite = loader.discover(start_dir, pattern='test_*.py')
    
    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Return exit code
    return 0 if result.wasSuccessful() else 1

if __name__ == '__main__':
    print("🧪 Running propER tests...")
    exit_code = run_tests()
    print(f"\n✅ Tests completed with exit code: {exit_code}")
    sys.exit(exit_code) 