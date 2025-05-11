# Momentum Book Management API

A RESTful API for managing a library's book collection and reader information. This API allows you to create and manage books and readers, handle book checkouts, and track book availability.

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

All database-modifying operations are wrapped in transactions to ensure data integrity.
