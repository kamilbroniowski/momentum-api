# Momentum Book Management API

A RESTful API for managing a library's book collection and reader information. This API allows you to create and manage books and readers, handle book checkouts, and track book availability.


### Author

Kamil Broniowski <kamil505@poczta.it>

## Prerequisites

- **Poetry v2.x is required** for dependency management and running the application. You must have Poetry v2 installed locally (v2.0.0 or newer).
- Docker and Docker Compose (for containerized setup)
- Python 3.10+ (for local development)

### Poetry v2 Installation/Upgrade

If you do not have Poetry v2, upgrade or install it with:

```bash
curl -sSL https://install.python-poetry.org | python3 -
poetry --version  # Should report version 2.x
```

If you previously installed Poetry with pip, uninstall it first:

```bash
pip uninstall poetry
```

## Getting Started

### Running with Docker Compose

The application is containerized and can be easily run using Docker Compose with PostgreSQL as the database.

1. Make sure you have Docker, Docker Compose, and **Poetry v2.x** installed on your system.
2. Create a `.env` file based on the provided `.env.sample` file:
   ```bash
   cp .env.sample .env
   ```
3. Start the application:
   ```bash
   docker compose up --build
   ```
4. The API will be available at http://localhost:8000/

### Development Setup (Local)

If you prefer to run the application locally:

1. Make sure you have **Poetry v2.x** installed:
   ```bash
   poetry --version  # Should report version 2.x
   ```
2. Install dependencies using Poetry:
   ```bash
   poetry install
   ```
3. Set up the PostgreSQL database and update the `.env` file with connection details
4. Run migrations:
   ```bash
   poetry run python library/manage.py migrate
   ```
5. Start the development server:
   ```bash
   poetry run python library/manage.py runserver
   ```

## Technology Stack

- **Python**: 3.13
- **Web Framework**: Django 5.2.1
- **API Framework**: Django REST Framework 3.16.0
- **Database**: PostgreSQL 15
- **Dependency Management**: Poetry 2.x
- **Static File Serving**: WhiteNoise 6.9.0
- **Testing**: pytest, pytest-django
- **Formatting & Linting**: Black
- **CI/CD**: Pre-commit hooks

## Project Architecture

The API follows a **separation of concerns** design pattern with three main components:

### 1. Serializers
- **BookSerializer** - CRUD operations for books
- **BookStatusSerializer** - Handle borrowing status updates
- **BookListSerializer** - Format book listings with status information
- **ReaderCreateSerializer** - Reader creation and validation

### 2. Services
- **create_book()** - Create new books with validation
- **get_all_books()** - Retrieve the book collection
- **delete_book()** - Remove books from the database
- **update_book_borrow_status()** - Handle book checkout/return logic

### 3. Views
- **BookListCreateAPIView (GET/POST)** - List all books and create new ones
- **BookDetailAPIView (GET/DELETE)** - View and delete individual books
- **BookStatusAPIView (PATCH)** - Update borrower status
- **ReaderCreateAPIView** - Create new reader accounts

## Project Structure

```
├── api/                # Book management API application
│   ├── migrations/     # Database migrations
│   ├── models.py       # Data models (Book, Reader)
│   ├── serializers.py  # Data validation and serialization
│   ├── services.py     # Business logic implementation
│   ├── signals.py      # Django signals for model events
│   ├── validators.py   # Custom field validators
│   └── views.py        # API endpoint definitions
├── library/            # Django project configuration
└── tests/              # Test suite
```

## Testing

The project includes a comprehensive test suite covering models, services, and API endpoints. Run tests with pytest:

```bash
poetry run pytest
```

Test settings use in-memory SQLite for faster test execution.

## Troubleshooting

- If you see errors like `poetry: command not found` or `poetry version < 2`, ensure you have installed Poetry v2 as described above.
- If you have both Poetry v1 and v2 installed, remove the old version to avoid conflicts.
- If Docker Compose fails due to missing dependencies, confirm that Poetry v2 is available inside your container image as well.

## API Endpoints

### Books

The book-related endpoints are implemented using a ViewSet, which provides multiple actions through a single endpoint.

#### List All Books

```
GET /books/
```

**Description**: Retrieve a list of all books in the library with their current status.

**Response**: 200 OK
```json
[
  {
    "serial_number": "123456",
    "title": "Book Title",
    "author": "Author Name",
    "status": "available",
    "borrower_serial_number": null,
    "borrow_date": null
  },
  {
    "serial_number": "123457",
    "title": "Another Book",
    "author": "Another Author",
    "status": "borrowed",
    "borrower_serial_number": "654321",
    "borrow_date": "2025-05-01T14:30:00Z"
  }
]
```

#### Create a New Book

```
POST /books/
```

**Description**: Add a new book to the library.

**Request Body**:
```json
{
  "serial_number": "123458",
  "title": "New Book",
  "author": "New Author"
}
```

**Response**: 201 Created
```json
{
  "serial_number": "123458",
  "title": "New Book",
  "author": "New Author"
}
```

**Error Responses**:
- 400 Bad Request: If the request body contains invalid data (e.g., invalid serial number format, missing required fields).

#### Get a Book by Serial Number

```
GET /books/{serial_number}/
```

**Description**: Retrieve detailed information about a specific book.

**Response**: 200 OK
```json
{
  "serial_number": "123456",
  "title": "Book Title",
  "author": "Author Name",
  "status": "available",
  "borrower_serial_number": null,
  "borrow_date": null
}
```

**Error Responses**:
- 404 Not Found: If no book with the specified serial number exists.

#### Delete a Book

```
DELETE /books/{serial_number}/
```

**Description**: Remove a book from the library.

**Response**: 204 No Content

**Error Responses**:
- 404 Not Found: If no book with the specified serial number exists.

#### Update Book Borrowing Status

```
PATCH /books/{serial_number}/status/
```

**Note**: The trailing slash is required by Django REST Framework.

**Description**: Update a book's borrowing status. Setting a borrower marks the book as borrowed. Setting the borrower to null marks the book as available.

**Request Body** (To borrow a book):
```json
{
  "borrower": "654321"  // Reader's serial number
}
```

**Request Body** (To return a book):
```json
{
  "borrower": null
}
```

**Response**: 200 OK
```json
{
  "serial_number": "123456",
  "title": "Book Title",
  "author": "Author Name",
  "status": "borrowed",
  "borrower_serial_number": "654321",
  "borrow_date": "2025-05-11T14:30:00Z"
}
```

**Error Responses**:
- 400 Bad Request: If the request body contains invalid data (e.g., non-existent reader).
- 404 Not Found: If no book with the specified serial number exists.

### Readers

#### Create a Reader

```
POST /readers/
```

**Description**: Create a new reader with a unique serial number.

**Request Body**:
```json
{
  "serial_number": "654321"
}
```

**Response**: 201 Created
```json
{
  "serial_number": "654321"
}
```

**Error Responses**:
- 400 Bad Request: If the serial number format is invalid.

## Data Models

### Book

- **serial_number**: String (6 digits)
- **title**: String
- **author**: String
- **borrower**: Reader (optional, foreign key)
- **borrow_date**: DateTime (optional)

### Reader

- **serial_number**: String (6 digits)

## Implementation Details

The API is implemented with Django REST Framework and follows a clean architecture with the following components:

- **Serializers**: Handle data validation and transformation
  - `BookSerializer`: For CRUD operations on books
  - `BookStatusSerializer`: For updating book borrowing status
  - `BookListSerializer`: For listing books with their status
  - `ReaderCreateSerializer`: For creating readers

- **Services**: Encapsulate business logic
  - `BookService`: Provides methods for book management
  - `create_reader`: Creates new readers

- **Views**: Handle HTTP requests
  - `BookViewSet`: Handles all book-related operations
  - `ReaderCreateAPIView`: Handles reader creation

All database-modifying operations are wrapped in transactions to ensure data integrity. The service layer handles all business logic and validation, keeping the views focused on HTTP concerns only.

## Development Practices

- **Code Formatting**: Black is used for consistent code formatting.
- **Transaction Safety**: All database-modifying operations use Django's transaction management.
- **Validation**: Input validation happens at multiple levels (serializers, services, models).
- **Testing**: All components have dedicated tests to ensure reliability.
