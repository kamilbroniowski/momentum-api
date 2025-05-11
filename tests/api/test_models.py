from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils import timezone
from api.models import Reader, Book


class ReaderModelIntegrationTest(TestCase):
    """Integration tests for the Reader model.

    Using Django's TestCase class for transaction management.
    """

    def test_bulk_create_readers(self):
        """Test bulk creation of Reader objects."""
        valid_serial_numbers = ["111111", "222222", "333333", "444444"]
        readers = [Reader(serial_number=sn) for sn in valid_serial_numbers]
        Reader.objects.bulk_create(readers)

        assert Reader.objects.count() == 4

    def test_filter_readers_by_serial_number(self):
        """Test filtering Reader objects by serial number."""
        valid_serial_numbers = ["111111", "222222", "333333", "444444"]
        readers = [Reader(serial_number=sn) for sn in valid_serial_numbers]
        Reader.objects.bulk_create(readers)

        filtered = Reader.objects.filter(serial_number__startswith="3")
        assert filtered.count() == 1
        assert filtered.first().serial_number == "333333"


class BookModelTest(TestCase):
    """focusing on model-specific aspects."""

    def setUp(self):
        """Set up test data for Book tests."""
        self.reader = Reader.objects.create(serial_number="123456")
        self.book = Book.objects.create(
            serial_number="987654", title="Test Book", author="Test Author"
        )

    def test_book_primary_key(self):
        """Test that serial_number functions as primary key."""
        pk_field = Book._meta.pk
        assert pk_field.name == "serial_number"

        retrieved_book = Book.objects.get(pk="987654")
        assert retrieved_book == self.book

    def test_book_required_fields(self):
        """Test validation for required fields."""
        required_fields = ["serial_number", "title", "author"]

        for field_name in required_fields:
            with self.subTest(field=field_name):
                book_data = {
                    "serial_number": "555555",
                    "title": "Test Title",
                    "author": "Test Author",
                }
                book_data.pop(field_name)

                book = Book(**book_data)
                with self.assertRaises(ValidationError):
                    book.full_clean()

    def test_book_optional_fields(self):
        """Test that optional fields can be null/blank."""
        book = Book(
            serial_number="444444",
            title="Optional Fields Book",
            author="Test Author",
            borrower=None,
            borrow_date=None,
        )
        book.full_clean()  # all fields are valid
        book.save()

        saved_book = Book.objects.get(serial_number="444444")
        assert saved_book.borrower is None
        assert saved_book.borrow_date is None

    def test_book_foreign_key_relationship(self):
        """Test the foreign key relationship between Book and Reader."""
        self.book.borrower = self.reader
        self.book.borrow_date = timezone.now()
        self.book.save()

        assert self.book.borrower.serial_number == "123456"

        related_books = self.reader.book_set.all()
        assert related_books.count() == 1
        assert related_books.first() == self.book

    def test_string_representation(self):
        """Test the string representation of the Book model."""
        expected_str = "987654 Test Book Test Author"
        assert str(self.book) == expected_str
