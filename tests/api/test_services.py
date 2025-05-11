import pytest
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
from api.services import create_reader, BookService
from api.models import Book, Reader


@pytest.mark.django_db
class TestCreateReader:
    def test_create_reader_success(self):
        serial_number = "123456"
        reader = create_reader(serial_number)

        assert reader.serial_number == serial_number
        assert Reader.objects.filter(serial_number=serial_number).exists()

    def test_create_reader_invalid_serial_number(self):
        invalid_serial_numbers = [
            "12345",
            "1234567",
            "abcdef",
            "12345a",
            "",
        ]

        for invalid_sn in invalid_serial_numbers:
            with pytest.raises(ValidationError):
                create_reader(invalid_sn)

        assert Reader.objects.count() == 0

    def test_create_reader_duplicate_serial_number(self):
        serial_number = "123456"
        create_reader(serial_number)

        with pytest.raises(ValidationError):
            create_reader(serial_number)

        assert Reader.objects.filter(serial_number=serial_number).count() == 1


@pytest.mark.django_db
class TestBookService:
    def test_create_book_success(self):
        serial_number = "123456"
        title = "Test Book"
        author = "Test Author"

        book = BookService.create_book(serial_number, title, author)

        assert book.serial_number == serial_number
        assert book.title == title
        assert book.author == author
        assert book.borrower is None
        assert book.borrow_date is None
        assert Book.objects.filter(serial_number=serial_number).exists()

    def test_create_book_invalid_serial_number(self):
        # Test creating a book with invalid serial number
        invalid_serial_numbers = [
            "12345",  # Too short
            "1234567",  # Too long
            "abcdef",  # Non-numeric
            "12345a",  # Mixed
            "",  # Empty
        ]

        for invalid_sn in invalid_serial_numbers:
            with pytest.raises(ValidationError):
                BookService.create_book(invalid_sn, "Test Book", "Test Author")

        assert Book.objects.count() == 0

    def test_create_book_duplicate_serial_number(self):
        serial_number = "123456"
        BookService.create_book(serial_number, "Test Book 1", "Test Author 1")

        with pytest.raises(ValidationError):
            BookService.create_book(serial_number, "Test Book 2", "Test Author 2")

        assert Book.objects.filter(serial_number=serial_number).count() == 1

    def test_get_all_books(self):
        BookService.create_book("123456", "Book 1", "Author 1")
        BookService.create_book("123457", "Book 2", "Author 2")
        BookService.create_book("123458", "Book 3", "Author 3")

        books = BookService.get_all()

        assert len(books) == 3
        assert set(book.serial_number for book in books) == {
            "123456",
            "123457",
            "123458",
        }

    def test_get_book_by_serial_exists(self):
        serial_number = "123456"
        title = "Test Book"
        author = "Test Author"

        BookService.create_book(serial_number, title, author)

        book = BookService.get_by_serial(serial_number)

        assert book is not None
        assert book.serial_number == serial_number
        assert book.title == title
        assert book.author == author

    def test_get_book_by_serial_not_exists(self):
        book = BookService.get_by_serial("999999")

        assert book is None

    def test_delete_book_exists(self):
        serial_number = "123456"
        BookService.create_book(serial_number, "Test Book", "Test Author")

        result = BookService.delete(serial_number)

        assert result is True
        assert not Book.objects.filter(serial_number=serial_number).exists()

    def test_delete_book_not_exists(self):
        result = BookService.delete("999999")

        assert result is False

    def test_update_book_borrow_status_to_borrowed(self):
        serial_number = "123456"
        book = BookService.create_book(serial_number, "Test Book", "Test Author")
        reader = create_reader("654321")

        updated_book = BookService.update_borrow_status(book, reader)

        book.refresh_from_db()

        assert updated_book.borrower == reader
        assert updated_book.borrow_date is not None
        assert book.borrower == reader
        assert book.borrow_date is not None

    def test_update_book_borrow_status_to_available(self):
        serial_number = "123456"
        book = BookService.create_book(serial_number, "Test Book", "Test Author")
        reader = create_reader("654321")

        book.borrower = reader
        book.borrow_date = timezone.now()
        book.save()

        updated_book = BookService.update_borrow_status(book, None)

        book.refresh_from_db()

        assert updated_book.borrower is None
        assert updated_book.borrow_date is None
        assert book.borrower is None
        assert book.borrow_date is None

    def test_update_book_borrow_status_change_borrower(self):
        serial_number = "123456"
        book = BookService.create_book(serial_number, "Test Book", "Test Author")
        reader1 = create_reader("654321")
        reader2 = create_reader("654322")

        # Set initial borrower
        book.borrower = reader1
        old_date = timezone.now() - timedelta(days=5)
        book.borrow_date = old_date
        book.save()

        # Change borrower
        updated_book = BookService.update_borrow_status(book, reader2)

        # Refresh from database
        book.refresh_from_db()

        assert updated_book.borrower == reader2
        assert updated_book.borrow_date > old_date
        assert book.borrower == reader2
        assert book.borrow_date > old_date
