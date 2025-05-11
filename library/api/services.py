from .models import Reader


def create_reader(serial_number):
    """
    Create a new reader with the serial number.

    Raises ValidationError if the serial number is not valid.
    """
    reader = Reader(serial_number=serial_number)
    reader.full_clean()
    reader.save()
    return reader
