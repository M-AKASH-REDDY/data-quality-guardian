# tests2/conftest.py
# Ensure the project root is on sys.path so "import dqg" works in tests.
import sys, os
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
