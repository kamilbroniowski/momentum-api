from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ReaderCreateAPIView, BookViewSet

# Create a router and register the ViewSet
router = DefaultRouter()
router.register(r"books", BookViewSet, basename="book")

# The API URLs are determined automatically by the router
urlpatterns = [
    path("readers/", ReaderCreateAPIView.as_view(), name="reader-create"),
    path("", include(router.urls)),
]
