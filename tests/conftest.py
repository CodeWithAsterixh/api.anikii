import os
import sys

# Add project root (api.anikii) to sys.path so tests can import the 'app' package
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
