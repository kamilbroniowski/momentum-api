# Import all settings from the main settings file
from library.settings import *

# Use an in-memory SQLite database for tests
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

# Don't use whitenoise in tests
MIDDLEWARE = [m for m in MIDDLEWARE if not m.startswith("whitenoise")]

# Faster password hasher for tests
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

# Turn off all debugging for tests
DEBUG = False
