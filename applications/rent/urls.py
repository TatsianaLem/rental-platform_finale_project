from rest_framework.routers import DefaultRouter
from django.urls import path, include
from applications.rent.views import RentViewSet, BookingViewSet, ReviewViewSet

router = DefaultRouter()
router.register(r'rents', RentViewSet, basename='rent')
router.register(r'bookings', BookingViewSet, basename='booking')
router.register(r"reviews", ReviewViewSet, basename="review")

urlpatterns = [
    path('', include(router.urls)),
] + router.urls
