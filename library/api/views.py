from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db import transaction
from .serializers import ReaderCreateSerializer


class ReaderCreateAPIView(APIView):
    """
    API view for creating a single reader with a serial number.
    """

    def post(self, request):
        """Handle POST requests to create a new reader with auto-generated serial number"""
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
