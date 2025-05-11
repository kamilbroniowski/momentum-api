from django.db.models.signals import post_delete
from django.dispatch import receiver

from .models import Reader, Book


@receiver(post_delete, sender=Reader)
def clear_borrow_date_on_reader_delete(sender, instance, **kwargs):
    """When a Reader is deleted, clear the borrow_date on their previously borrowed books.

    This ONLY handles the specific case of Reader deletion.
    """
    Book.objects.filter(borrower__isnull=True, borrow_date__isnull=False).update(
        borrow_date=None
    )
