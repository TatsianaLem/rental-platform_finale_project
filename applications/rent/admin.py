from django.contrib import admin, messages
from django.utils import timezone
from applications.rent.models import Rent, Booking

class PriceRangeFilter(admin.SimpleListFilter):
    title = "Price range"
    parameter_name = "price_range"

    def lookups(self, request, model_admin):
        return [
            ("<500", "Less than 500 €"),
            ("500-1000", "500 € – 1000 €"),
            ("1000-1500", "1000 € – 1500 €"),
            (">1500", "More than 1500 €"),
        ]

    def queryset(self, request, queryset):
        value = self.value()
        if value == "<500":
            return queryset.filter(price__lt=500)
        if value == "500-1000":
            return queryset.filter(price__gte=500, price__lte=1000)
        if value == "1000-1500":
            return queryset.filter(price__gte=1000, price__lte=1500)
        if value == ">1500":
            return queryset.filter(price__gt=1500)
        return queryset

@admin.register(Rent)
class RentAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "owner",
        "city",
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
        "room_type",
        "rooms_count",
        "address",
        PriceRangeFilter,
    )
    search_fields = ("title", "address", "owner__email")

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