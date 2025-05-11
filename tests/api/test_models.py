from django.test import TestCase
from api.models import Reader


class ReaderModelIntegrationTest(TestCase):
    """Integration tests for the Reader model.

    Using Django's TestCase class for transaction management.
    """

    def test_bulk_create_readers(self):
        """Test bulk creation of Reader objects."""
        valid_serial_numbers = ["111111", "222222", "333333", "444444"]
        readers = [Reader(serial_number=sn) for sn in valid_serial_numbers]
        Reader.objects.bulk_create(readers)

        assert Reader.objects.count() == 4

    def test_filter_readers_by_serial_number(self):
        """Test filtering Reader objects by serial number."""
        valid_serial_numbers = ["111111", "222222", "333333", "444444"]
        readers = [Reader(serial_number=sn) for sn in valid_serial_numbers]
        Reader.objects.bulk_create(readers)

        filtered = Reader.objects.filter(serial_number__startswith="3")
        assert filtered.count() == 1
        assert filtered.first().serial_number == "333333"
