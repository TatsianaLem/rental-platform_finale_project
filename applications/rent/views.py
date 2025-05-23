from rest_framework import viewsets, permissions, filters, status
from applications.rent.models import Rent, Booking
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from applications.rent.permissions import IsOwnerOrStaff, IsLandlordOrReadOnly
from applications.rent.serializers import RentSerializer, BookingSerializer
from django_filters.rest_framework import DjangoFilterBackend
from applications.rent.filters import RentFilter


class RentViewSet(viewsets.ModelViewSet):
    queryset = Rent.objects.all()
    serializer_class = RentSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        IsOwnerOrStaff,
        IsLandlordOrReadOnly
    ]

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = RentFilter
    search_fields = ['title', 'description']
    ordering_fields = ['price', 'created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        if self.request.user.is_staff:
            return Rent.objects.all()
        return Rent.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == "LANDLORD":
            return Booking.objects.filter(rent__owner=user)
        return Booking.objects.filter(tenant=user)

    def perform_create(self, serializer):
        serializer.save(tenant=self.request.user)

    @action(detail=True, methods=["patch"], url_path="cancel")
    def cancel_booking(self, request, pk=None):
        booking = self.get_object()

        if request.user != booking.tenant:
            return Response({"detail": "Только арендатор может отменить бронь."}, status=403)

        if not booking.can_cancel():
            return Response({"detail": "Нельзя отменить бронь за день до заезда."}, status=400)

        booking.status = Booking.Status.CANCELLED
        booking.save()
        return Response({"status": "Бронирование отменено."}, status=200)

    @action(detail=True, methods=["patch"], url_path="confirm")
    def confirm_booking(self, request, pk=None):
        booking = self.get_object()

        if request.user != booking.rent.owner:
            return Response({"detail": "Только арендодатель может подтверждать бронь."}, status=403)

        if booking.status != Booking.Status.PENDING:
            return Response({"detail": "Бронь уже обработана."}, status=400)

        booking.status = Booking.Status.CONFIRMED
        booking.save()
        return Response({"status": "Бронирование подтверждено."}, status=200)

    @action(detail=True, methods=["patch"], url_path="decline")
    def decline_booking(self, request, pk=None):
        booking = self.get_object()

        if request.user != booking.rent.owner:
            return Response({"detail": "Только арендодатель может отклонить бронь."}, status=403)

        if booking.status != Booking.Status.PENDING:
            return Response({"detail": "Бронь уже обработана."}, status=400)

        booking.status = Booking.Status.DECLINED
        booking.save()
        return Response({"status": "Бронирование отклонено."}, status=200)

