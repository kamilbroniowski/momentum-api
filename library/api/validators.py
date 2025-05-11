from django.core.validators import RegexValidator

six_number_digits_validator = RegexValidator(
    regex=r"^\d{6}$",
    message="Serial number must be exactly 6 digits.",
    code="invalid_serial_number",
)
