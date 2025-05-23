from rest_framework.routers import DefaultRouter
from django.urls import path, include
from applications.rent.views import RentViewSet, BookingViewSet

router = DefaultRouter()
router.register(r'rents', RentViewSet, basename='rent')
router.register(r'bookings', BookingViewSet, basename='booking')

urlpatterns = [
    path('', include(router.urls)),
]
