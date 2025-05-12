import os
import sys
import pytest

# Add the project root directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure Django settings for tests
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "library.settings")

# For in-memory SQLite database during tests
os.environ.setdefault("TEST_DATABASE", "sqlite")

# Import Django and setup
import django

django.setup()
