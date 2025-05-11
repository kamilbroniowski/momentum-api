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

    borrower = serializers.SerializerMethodField()

    class Meta:
        model = Book
        fields = ["serial_number", "title", "author", "borrower", "borrow_date"]
        read_only_fields = ["borrow_date"]

    def get_borrower(self, obj):
        """Return the borrower's serial number instead of ID"""
        if obj.borrower:
            return obj.borrower.serial_number
        return None

    def create(self, validated_data):
        """Handle case where borrower is sent as serial number string"""
        # Remove borrower from validated_data if present, as we handle it separately
        borrower_serial = validated_data.pop("borrower", None)

        # Create the book
        book = Book.objects.create(**validated_data)

        # Set borrower if provided
        if borrower_serial:
            try:
                book.borrower = Reader.objects.get(serial_number=borrower_serial)
                book.save()
            except Reader.DoesNotExist:
                pass

        return book


class BookStatusSerializer(serializers.ModelSerializer):
    """
    Serializer for updating book status (borrowed/available).
    Only allows updating the borrower field.
    """

    borrower = serializers.CharField(required=False, allow_null=True)

    class Meta:
        model = Book
        fields = ["borrower"]

    def validate_borrower(self, value):
        """Validate borrower by converting serial number to Reader object"""
        if value is None:
            return None

        try:
            return Reader.objects.get(serial_number=value)
        except Reader.DoesNotExist:
            raise serializers.ValidationError(
                f"Reader with serial number '{value}' not found."
            )

    def to_internal_value(self, data):
        """Handle both null and string cases for borrower"""
        if "borrower" in data and data["borrower"] is None:
            # Handle explicit null case
            return {"borrower": None}
        return super().to_internal_value(data)


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
