from rest_framework import serializers

from .models import Reader, Book


class ReaderCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a new reader.
    """

    class Meta:
        model = Reader
        fields = ["serial_number"]


class BookSerializer(serializers.ModelSerializer):
    """
    Serializer for book operations (create, retrieve, list, update, delete).
    """

    class Meta:
        model = Book
        fields = ["serial_number", "title", "author", "borrower", "borrow_date"]
        read_only_fields = ["borrow_date"]


class BookStatusSerializer(serializers.ModelSerializer):
    """
    Serializer for updating book status (borrowed/available).
    Only allows updating the borrower field.
    """

    class Meta:
        model = Book
        fields = ["borrower"]


class BookListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing books with borrower information.
    """

    status = serializers.SerializerMethodField()
    borrower_serial_number = serializers.SerializerMethodField()

    class Meta:
        model = Book
        fields = [
            "serial_number",
            "title",
            "author",
            "status",
            "borrower_serial_number",
            "borrow_date",
        ]

    def get_status(self, obj):
        return "borrowed" if obj.borrower else "available"

    def get_borrower_serial_number(self, obj):
        return obj.borrower.serial_number if obj.borrower else None
