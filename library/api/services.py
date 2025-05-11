from django.utils import timezone
from django.db import transaction
from .models import Reader, Book


def create_reader(serial_number):
    """
    Create a new reader with the serial number.

    Raises ValidationError if the serial number is not valid.
    """
    reader = Reader(serial_number=serial_number)
    reader.full_clean()
    reader.save()
    return reader


class BookService:
    @staticmethod
    @transaction.atomic
    def create_book(serial_number, title, author):
        """
        Create a new book with the given details.

        Raises ValidationError if the serial number is not valid.
        """
        book = Book(serial_number=serial_number, title=title, author=author)
        book.full_clean()
        book.save()
        return book

    @staticmethod
    def get_all():
        """
        Retrieve all books in the library.
        """
        return Book.objects.all()

    @staticmethod
    def get_by_serial(serial_number):
        """
        Get a book by its serial number or None if not found.
        """
        try:
            return Book.objects.get(serial_number=serial_number)
        except Book.DoesNotExist:
            return None

    @staticmethod
    @transaction.atomic
    def delete(serial_number):
        """
        Delete a book by its serial number.
        Returns True if deleted, False if not found.
        """
        book = BookService.get_by_serial(serial_number)
        if book:
            book.delete()
            return True
        return False

    @staticmethod
    @transaction.atomic
    def update_borrow_status(book, borrower=None):
        """
        Update book's status to borrowed or available.
        If borrower is provided, book is borrowed.
        If borrower is None, book is marked as available.

        Returns updated book.
        """
        if borrower:
            # Setting borrower (book is borrowed)
            book.borrower = borrower
            book.borrow_date = timezone.now()
        else:
            # Clearing borrower (book is available)
            book.borrower = None
            book.borrow_date = None

        book.save()
        return book
