from rest_framework import serializers

from .models import Reader


class ReaderCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a new reader.
    """

    class Meta:
        model = Reader
        fields = ["serial_number"]
