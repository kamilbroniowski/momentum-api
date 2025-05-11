import pytest
from django.core.exceptions import ValidationError
from api.services import create_reader
from api.models import Reader


@pytest.mark.django_db
class TestCreateReader:
    def test_create_reader_success(self):
        serial_number = "123456"
        reader = create_reader(serial_number)

        assert reader.serial_number == serial_number
        assert Reader.objects.filter(serial_number=serial_number).exists()

    def test_create_reader_invalid_serial_number(self):
        invalid_serial_numbers = [
            "12345",
            "1234567",
            "abcdef",
            "12345a",
            "",
        ]

        for invalid_sn in invalid_serial_numbers:
            with pytest.raises(ValidationError):
                create_reader(invalid_sn)

        assert Reader.objects.count() == 0

    def test_create_reader_duplicate_serial_number(self):
        serial_number = "123456"
        create_reader(serial_number)

        with pytest.raises(ValidationError):
            create_reader(serial_number)

        assert Reader.objects.filter(serial_number=serial_number).count() == 1
