from django.forms import ValidationError
import pytest

from api.validators import six_number_digits_validator


@pytest.mark.parametrize("serial_number", ["123456", "654321", "000000"])
def test_six_digits_validator_passes(serial_number):
    six_number_digits_validator(serial_number)


@pytest.mark.parametrize("serial_number", ["abcdef", "1234567", "12345a"])
def test_six_digits_validator_throws_validation_error(serial_number):
    with pytest.raises(ValidationError):
        six_number_digits_validator(serial_number)
