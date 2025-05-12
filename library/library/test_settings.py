from .settings import *

# Override database configuration for testing
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",  # In-memory SQLite database for tests
    }
}
