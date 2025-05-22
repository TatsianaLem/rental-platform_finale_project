from rest_framework.routers import DefaultRouter
from django.urls import path, include
from applications.rent.views import RentViewSet

router = DefaultRouter()
router.register(r'rents', RentViewSet, basename='rent')

urlpatterns = [
    path('', include(router.urls)),
]
