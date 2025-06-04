from django.db.models import Avg, Q
from rest_framework import viewsets, permissions, filters, status
from applications.rent.models import Rent, Booking
from applications.rent.models.review import Review
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from applications.rent.permissions import (
    IsOwnerOrStaff,
    IsLandlordOrReadOnly,
    IsBookingParticipant,
)
from applications.rent.serializers import (
    RentSerializer,
    BookingSerializer,
    ReviewSerializer,
)
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
    search_fields = ['title', 'description', 'address']
    filterset_fields = ['city', 'room_type', 'rooms_count']
    ordering_fields = ['price', 'created_at', 'avg_rating']
    ordering = ['-created_at']

    def get_queryset(self):
        user = self.request.user
        qs = Rent.objects.annotate(avg_rating=Avg("reviews__rating"))

        search = self.request.query_params.get("search")
        if search:
            qs = qs.filter(Q(title__icontains=search) | Q(description__icontains=search))

        ordering = self.request.query_params.get("ordering")

        if ordering in ["avg_rating", "-avg_rating"]:
            qs = qs.filter(avg_rating__isnull=False)

        if user.is_superuser or user.is_staff:
            return qs

        if user.is_authenticated:
            if hasattr(user, "role"):
                if user.role == "LANDLORD":
                    return qs.filter(owner=user)
                elif user.role == "TENANT":
                    return qs.filter(is_active=True)

        return qs.filter(is_active=True)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

class BookingViewSet(viewsets.ModelViewSet):
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated, IsBookingParticipant]

    def get_queryset(self):
        user = self.request.user

        if user.is_superuser:
            return Booking.objects.all()

        if user.is_authenticated:
            if hasattr(user, "role") and user.role == "LANDLORD":
                return Booking.objects.filter(rent__owner=user)
            return Booking.objects.filter(tenant=user)

        return Booking.objects.none()

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

    @action(detail=True, methods=["patch", "post"], url_path="decline")
    def decline_booking(self, request, pk=None):
        booking = self.get_object()

        if request.user != booking.rent.owner:
            return Response({"detail": "Только арендодатель может отклонить бронь."}, status=403)

        if booking.status != Booking.Status.PENDING:
            return Response({"detail": "Бронь уже обработана."}, status=400)

        booking.status = Booking.Status.DECLINED
        booking.save()
        return Response({"status": "Бронирование отклонено."}, status=200)

class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        review = serializer.save(author=self.request.user)
        review.clean()
