from django.contrib import admin, messages
from django.utils import timezone
from applications.rent.models import Rent, Booking
from applications.rent.filters import (
    CityListFilter,
    RoomTypeFilter,
    RoomsCountFilter,
    PriceRangeDropdownFilter,
)


@admin.register(Rent)
class RentAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "owner",
        "city",
        #"price",
        "address",
        "price_display",
        "rooms_count",
        "room_type",
        # "latitude",
        # "longitude",
        "is_active",
        "created_at",
    )
    list_filter = (
        "is_active",
        CityListFilter,
        RoomTypeFilter,
        RoomsCountFilter,
        PriceRangeDropdownFilter,
    )
    search_fields = ("title", "address", "city", "owner__email")

    def price_display(self, obj):
        return f"{obj.price} € / month"

    price_display.short_description = "Price"

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("rent", "tenant", "check_in", "check_out", "status")
    list_filter = ("status",)
    search_fields = ("rent__title", "tenant__email")
    actions = ["confirm_booking", "decline_booking", "cancel_booking"]

    def confirm_booking(self, request, queryset):
        count = 0
        for booking in queryset:
            if booking.status != Booking.Status.PENDING:
                continue
            if booking.rent.owner != request.user:
                continue
            booking.status = Booking.Status.CONFIRMED
            booking.save()
            count += 1
        self.message_user(request, f"{count} бронирований подтверждено.", messages.SUCCESS)

    confirm_booking.short_description = "✅ Подтвердить бронирование"

    def decline_booking(self, request, queryset):
        count = 0
        for booking in queryset:
            if booking.status != Booking.Status.PENDING:
                continue
            if booking.rent.owner != request.user:
                continue
            booking.status = Booking.Status.DECLINED
            booking.save()
            count += 1
        self.message_user(request, f"{count} бронирований отклонено.", messages.WARNING)

    decline_booking.short_description = "❌ Отклонить бронирование"

    def cancel_booking(self, request, queryset):
        count = 0
        for booking in queryset:
            if booking.tenant != request.user:
                continue
            if not booking.can_cancel():
                continue
            booking.status = Booking.Status.CANCELLED
            booking.save()
            count += 1
        self.message_user(request, f"{count} бронирований отменено.", messages.INFO)

    cancel_booking.short_description = "🔁 Отменить бронирование (до заезда)"