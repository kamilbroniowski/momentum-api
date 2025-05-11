from django.db import models
from .validators import six_number_digits_validator

# Create your models here.


class Reader(models.Model):
    serial_number = models.CharField(
        max_length=6, validators=[six_number_digits_validator], unique=True
    )

    def __str__(self):
        return self.serial_number
