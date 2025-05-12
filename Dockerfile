FROM python:3.13-slim

WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=library.settings

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry~=2.1

# Copy only the files needed for installing dependencies
COPY pyproject.toml poetry.lock* ./

# Configure Poetry to not create a virtual environment
RUN poetry config virtualenvs.create false

# Install dependencies and add gunicorn
RUN poetry install --no-root --without dev --no-interaction --no-ansi && \
    pip install gunicorn

# Copy project files
COPY . .

# Create a non-root user to run the application
RUN useradd -m appuser && \
    mkdir -p /app/library/data /app/library/static /app/library/media && \
    chown -R appuser:appuser /app && \
    chown -R appuser:appuser /app/library/data /app/library/static /app/library/media

USER appuser

# Set the working directory to the Django project directory
WORKDIR /app/library

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application
CMD ["gunicorn", "library.wsgi:application", "--bind", "0.0.0.0:8000"]
