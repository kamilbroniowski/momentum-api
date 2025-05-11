from django.urls import path
from .views import ReaderCreateAPIView

urlpatterns = [
    path("readers/", ReaderCreateAPIView.as_view(), name="reader-create"),
]
