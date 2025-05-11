# tests/api/test_views.py

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.utils import timezone
from datetime import timedelta

from api.models import Reader, Book
from api.services import create_reader, BookService


@pytest.mark.django_db
class TestReaderCreateAPIView:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.client = APIClient()
        self.url = reverse("reader-create")

    def test_create_reader_success(self):
        """
        POST /readers/ with serial number returns 201 and serial number
        """
        data = {"serial_number": "123456"}
        response = self.client.post(self.url, data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["serial_number"] == "123456"
        assert Reader.objects.filter(serial_number="123456").exists()

    def test_create_reader_with_invalid_serial_number(self):
        """
        POST /readers/ with invalid serial number returns 400 Bad Request
        """
        data = {"serial_number": "12345a"}
        response = self.client.post(self.url, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "serial_number" in response.data

    @pytest.mark.parametrize(
        "method, expected_status",
        [
            ("delete", status.HTTP_405_METHOD_NOT_ALLOWED),
            ("put", status.HTTP_405_METHOD_NOT_ALLOWED),
            ("get", status.HTTP_405_METHOD_NOT_ALLOWED),
        ],
    )
    def test_reader_methods_not_allowed(self, method, expected_status):
        """
        Methods DELETE, PUT, GET on /readers/ return 405 Method Not Allowed
        """
        client_method = getattr(self.client, method)
        response = client_method(self.url)
        assert response.status_code == expected_status


@pytest.mark.django_db
class TestBookViewSetList:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.client = APIClient()
        self.url = reverse("book-list")

        # Create test books
        self.book1 = BookService.create_book("123456", "Test Book 1", "Test Author 1")
        self.book2 = BookService.create_book("123457", "Test Book 2", "Test Author 2")

        # Create reader and set book1 as borrowed
        self.reader = create_reader("654321")
        self.book1.borrower = self.reader
        self.book1.borrow_date = timezone.now()
        self.book1.save()

    def test_list_books(self):
        """
        GET /books/ returns a list of all books with their status
        """
        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2

        # Check first book (borrowed)
        book1_data = next(
            item for item in response.data if item["serial_number"] == "123456"
        )
        assert book1_data["title"] == "Test Book 1"
        assert book1_data["author"] == "Test Author 1"
        assert book1_data["status"] == "borrowed"
        assert book1_data["borrower_serial_number"] == "654321"
        assert book1_data["borrow_date"] is not None

        # Check second book (available)
        book2_data = next(
            item for item in response.data if item["serial_number"] == "123457"
        )
        assert book2_data["title"] == "Test Book 2"
        assert book2_data["author"] == "Test Author 2"
        assert book2_data["status"] == "available"
        assert book2_data["borrower_serial_number"] is None
        assert book2_data["borrow_date"] is None


@pytest.mark.django_db
class TestBookViewSetCreate:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.client = APIClient()
        self.url = reverse("book-list")

    def test_create_book_success(self):
        """
        POST /books/ with valid data returns 201 and the created book
        """
        data = {"serial_number": "123458", "title": "New Book", "author": "New Author"}
        response = self.client.post(self.url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["serial_number"] == "123458"
        assert response.data["title"] == "New Book"
        assert response.data["author"] == "New Author"
        assert Book.objects.filter(serial_number="123458").exists()

    def test_create_book_invalid_data(self):
        """
        POST /books/ with invalid data returns 400
        """
        # Missing title
        data = {"serial_number": "123458", "author": "New Author"}
        response = self.client.post(self.url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "title" in response.data

        # Invalid serial number
        data = {
            "serial_number": "1234",  # Too short
            "title": "New Book",
            "author": "New Author",
        }
        response = self.client.post(self.url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "serial_number" in response.data

    def test_create_book_duplicate_serial(self):
        """
        POST /books/ with duplicate serial number returns 400
        """
        # First create a book
        BookService.create_book("123456", "Existing Book", "Existing Author")

        # Try to create another with the same serial
        data = {"serial_number": "123456", "title": "New Book", "author": "New Author"}
        response = self.client.post(self.url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "serial_number" in response.data


@pytest.mark.django_db
class TestBookViewSetRetrieve:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.client = APIClient()
        self.book = BookService.create_book("123456", "Test Book", "Test Author")
        self.url = reverse("book-detail", kwargs={"pk": self.book.serial_number})

    def test_retrieve_book_success(self):
        """
        GET /books/{serial_number}/ returns book details
        """
        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["serial_number"] == "123456"
        assert response.data["title"] == "Test Book"
        assert response.data["author"] == "Test Author"

    def test_retrieve_book_not_found(self):
        """
        GET /books/{serial_number}/ with non-existent serial returns 404
        """
        url = reverse("book-detail", kwargs={"pk": "999999"})
        response = self.client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestBookViewSetDestroy:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.client = APIClient()
        self.book = BookService.create_book("123456", "Test Book", "Test Author")
        self.url = reverse("book-detail", kwargs={"pk": self.book.serial_number})

    def test_delete_book_success(self):
        """
        DELETE /books/{serial_number}/ removes the book
        """
        response = self.client.delete(self.url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Book.objects.filter(serial_number="123456").exists()

    def test_delete_book_not_found(self):
        """
        DELETE /books/{serial_number}/ with non-existent serial returns 404
        """
        url = reverse("book-detail", kwargs={"pk": "999999"})
        response = self.client.delete(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestBookViewSetStatus:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.client = APIClient()
        self.book = BookService.create_book("123456", "Test Book", "Test Author")
        self.reader = create_reader("654321")
        self.url = reverse("book-status", kwargs={"pk": self.book.serial_number})

    def test_update_status_to_borrowed(self):
        """
        PATCH /books/{serial_number}/status/ sets book as borrowed
        """
        data = {"borrower": self.reader.serial_number}
        response = self.client.patch(self.url, data, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["status"] == "borrowed"
        assert response.data["borrower_serial_number"] == self.reader.serial_number
        assert response.data["borrow_date"] is not None

        # Verify database was updated
        self.book.refresh_from_db()
        assert self.book.borrower == self.reader
        assert self.book.borrow_date is not None

    def test_update_status_to_available(self):
        """
        PATCH /books/{serial_number}/status/ sets book as available
        """
        # First set as borrowed
        self.book.borrower = self.reader
        self.book.borrow_date = timezone.now()
        self.book.save()

        # Then set as available
        data = {"borrower": None}
        response = self.client.patch(self.url, data, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["status"] == "available"
        assert response.data["borrower_serial_number"] is None
        assert response.data["borrow_date"] is None

        # Verify database was updated
        self.book.refresh_from_db()
        assert self.book.borrower is None
        assert self.book.borrow_date is None

    def test_update_status_change_borrower(self):
        """
        PATCH /books/{serial_number}/status/ changes book's borrower
        """
        # Create another reader
        reader2 = create_reader("654322")

        # First set as borrowed by reader 1
        self.book.borrower = self.reader
        old_date = timezone.now() - timedelta(days=5)
        self.book.borrow_date = old_date
        self.book.save()

        # Then change borrower to reader 2
        data = {"borrower": reader2.serial_number}
        response = self.client.patch(self.url, data, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["status"] == "borrowed"
        assert response.data["borrower_serial_number"] == reader2.serial_number

        # Verify database was updated with new borrower and more recent date
        self.book.refresh_from_db()
        assert self.book.borrower == reader2
        assert self.book.borrow_date > old_date

    def test_update_status_book_not_found(self):
        """
        PATCH /books/{serial_number}/status/ with non-existent serial returns 404
        """
        url = reverse("book-status", kwargs={"pk": "999999"})
        data = {"borrower": self.reader.serial_number}
        response = self.client.patch(url, data, format="json")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_status_invalid_reader(self):
        """
        PATCH /books/{serial_number}/status/ with non-existent reader returns 400
        """
        data = {"borrower": "999999"}  # Non-existent reader
        response = self.client.patch(self.url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "borrower" in response.data
