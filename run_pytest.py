#!/usr/bin/env python
# coding: utf-8

from __future__ import print_function, unicode_literals, absolute_import

import sys

import pytest

print("sys.real_prefix:", getattr(sys, "real_prefix", "-"))
print("sys.prefix:", sys.prefix)

if __name__ == "__main__":
    sys.stderr = sys.stdout
    pytest.main()
