#!/usr/bin/env python3

"""
    Helper to start pytest with arguments
"""

import sys

import pytest

print("sys.real_prefix:", getattr(sys, "real_prefix", "-"))
print("sys.prefix:", sys.prefix)

if __name__ == "__main__":
    # sys.stderr = sys.stdout #
    pytest.main()
