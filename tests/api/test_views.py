# tests/test_views.py

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

# Adjust this import path to your Reader model location
from api.models import Reader


@pytest.mark.django_db
class TestReaderCreateAPIView:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.client = APIClient()
        self.url = reverse("reader-create")

    def test_create_reader_returns_serial_number(self):
        """
        POST /readers/ with with serial number returns 201 and serial number
        """
        data = {"serial_number": "123456"}
        response = self.client.post(self.url, data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["serial_number"] == "123456"
        assert Reader.objects.filter(serial_number="123456").exists()

    def test_read_reader_returns_method_unallowed(self):
        """
        GET /readers/ returns 405 Method Not Allowed
        """
        response = self.client.get(self.url)
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_create_reader_with_invalid_serial_number(self):
        """
        POST /readers/ with invalid serial number returns 400 Bad Request
        """
        data = {"serial_number": "12345a"}
        response = self.client.post(self.url, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "serial_number" in response.data

    def test_delete_reader_returns_method_unallowed(self):
        """
        DELETE /readers/ returns 405 Method Not Allowed
        """
        response = self.client.delete(self.url)
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_update_reader_returns_method_unallowed(self):
        """
        PUT /readers/ returns 405 Method Not Allowed
        """
        response = self.client.put(self.url)
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
