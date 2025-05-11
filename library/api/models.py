from django.db import models
from .validators import six_number_digits_validator

# Create your models here.


class Reader(models.Model):
    serial_number = models.CharField(
        max_length=6, validators=[six_number_digits_validator], unique=True
    )

    def __str__(self):
        return self.serial_number


class Book(models.Model):
    serial_number = models.CharField(
        max_length=6,
        validators=[six_number_digits_validator],
        unique=True,
        primary_key=True,
    )
    title = models.CharField(max_length=100)
    author = models.CharField(max_length=100)
    borrower = models.ForeignKey(
        Reader, on_delete=models.SET_NULL, null=True, blank=True
    )
    borrow_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.serial_number} {self.title} {self.author}"
