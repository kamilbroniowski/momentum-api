from rest_framework import status, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db import transaction
from rest_framework.exceptions import NotFound

from .serializers import (
    ReaderCreateSerializer,
    BookSerializer,
    BookStatusSerializer,
    BookListSerializer,
)
from .services import BookService


class ReaderCreateAPIView(APIView):
    """
    API view for creating a single reader with a serial number.
    """

    def post(self, request):
        """POST to create a new reader with autogen serial number (if not provided)"""
        serializer = ReaderCreateSerializer(data=request.data)
        if serializer.is_valid():
            with transaction.atomic():
                reader = serializer.save()
            return Response(
                {"serial_number": reader.serial_number},
                status=status.HTTP_201_CREATED,
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )


class BookViewSet(viewsets.ViewSet):
    """
    ViewSet for book operations.

    list:
    Return a list of all books

    retrieve:
    Return a specific book by serial number

    create:
    Create a new book

    destroy:
    Delete a specific book by serial number

    update_status:
    Update a book's borrowing status
    """

    def get_object(self, serial_number):
        """Helper method to get book object or raise 404 if not found"""
        book = BookService.get_by_serial(serial_number)
        if not book:
            raise NotFound(f"Book with serial number {serial_number} not found")
        return book

    def list(self, request):
        """Get a list of all books"""
        books = BookService.get_all()
        serializer = BookListSerializer(books, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        """Get a specific book by serial number"""
        book = self.get_object(pk)
        serializer = BookSerializer(book)
        return Response(serializer.data)

    def create(self, request):
        """Create a new book"""
        serializer = BookSerializer(data=request.data)
        if serializer.is_valid():
            with transaction.atomic():
                # Use the data from the serializer to call the service function
                book = BookService.create_book(
                    serial_number=serializer.validated_data["serial_number"],
                    title=serializer.validated_data["title"],
                    author=serializer.validated_data["author"],
                )
            return Response(BookSerializer(book).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        """Delete a book"""
        success = BookService.delete(pk)
        if success:
            return Response(status=status.HTTP_204_NO_CONTENT)
        raise NotFound(f"Book with serial number {pk} not found")

    @action(detail=True, methods=["patch"])
    def status(self, request, pk=None):
        """Update book's borrow status"""
        book = self.get_object(pk)
        serializer = BookStatusSerializer(book, data=request.data, partial=True)

        if serializer.is_valid():
            with transaction.atomic():
                updated_book = BookService.update_borrow_status(
                    book=book, borrower=serializer.validated_data.get("borrower")
                )

            return Response(BookListSerializer(updated_book).data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
