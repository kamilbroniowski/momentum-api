from django.test import TestCase
from django.utils import timezone
from api.models import Reader, Book


class ReaderSignalsTest(TestCase):
    """Tests for signal handlers related to Reader model."""

    def setUp(self):
        """Set up test data."""
        self.reader = Reader.objects.create(serial_number="123456")
        self.book = Book.objects.create(
            serial_number="987654", title="Test Book", author="Test Author"
        )

    def test_on_delete_behavior(self):
        """Test foreign key on_delete behavior (SET_NULL) and clearing of borrow_date."""
        # Set a borrow date when creating a book with a borrower
        borrow_date = timezone.now()
        book = Book.objects.create(
            serial_number="111222",
            title="On Delete Test Book",
            author="Test Author",
            borrower=self.reader,
            borrow_date=borrow_date,
        )

        # Verify initial state
        assert book.borrower == self.reader
        assert book.borrow_date == borrow_date

        # Delete the reader
        self.reader.delete()
        book.refresh_from_db()

        # Verify both borrower and borrow_date are cleared
        assert book.borrower is None
        assert book.borrow_date is None
        assert Book.objects.filter(serial_number="111222").exists()
