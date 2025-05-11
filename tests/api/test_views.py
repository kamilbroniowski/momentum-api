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

    def test_create_reader_success(self):
        """
        POST /readers/ with with serial number returns 201 and serial number
        """
        data = {"serial_number": "123456"}
        response = self.client.post(self.url, data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["serial_number"] == "123456"
        assert Reader.objects.filter(serial_number="123456").exists()

    def test_create_reader_with_invalid_serial_number(self):
        """
        POST /readers/ with invalid serial number returns 400 Bad Request
        """
        data = {"serial_number": "12345a"}
        response = self.client.post(self.url, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "serial_number" in response.data

    @pytest.mark.parametrize(
        "method, expected_status",
        [
            ("delete", status.HTTP_405_METHOD_NOT_ALLOWED),
            ("put", status.HTTP_405_METHOD_NOT_ALLOWED),
            ("get", status.HTTP_405_METHOD_NOT_ALLOWED),
        ],
    )
    def test_reader_methods_not_allowed(self, method, expected_status):
        """
        Methods DELETE, PUT, GET on /readers/ return 405 Method Not Allowed
        """
        client_method = getattr(self.client, method)
        response = client_method(self.url)
        assert response.status_code == expected_status
