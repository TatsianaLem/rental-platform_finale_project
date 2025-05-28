from django.contrib import admin, messages
from django.db.models import Avg
from django.utils import timezone
from django.contrib.admin.models import LogEntry, CHANGE
from django.utils.html import format_html
from django.utils.encoding import force_str
from django.contrib.contenttypes.models import ContentType
from applications.rent.models import Rent, Booking, Review
from applications.rent.filters import (
    CityListFilter,
    RoomTypeFilter,
    RoomsCountFilter,
    PriceRangeDropdownFilter,
)
from applications.user.choices.roles import UserRole


class ReviewInline(admin.TabularInline):
    model = Review
    extra = 0
    readonly_fields = ("author", "created_at")
    fields = ("author", "rating", "comment", "created_at")
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False

@admin.register(Rent)
class RentAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "owner", "city", "price_display",
        "rooms_count", "room_type", "is_active", "created_at", "average_rating",
        #"price", "latitude", "longitude", "address",
    )
    list_filter = (
        "is_active",
        CityListFilter,
        RoomTypeFilter,
        RoomsCountFilter,
        PriceRangeDropdownFilter,
    )
    search_fields = ("title", "address", "city", "owner__email")
    inlines = [ReviewInline]


    def get_queryset(self, request):
        qs = super().get_queryset(request)
        user = request.user

        if user.is_superuser:
            return qs

        if hasattr(user, "role"):
            if user.role == "LANDLORD":
                return qs.filter(owner=user)
            elif user.role == "TENANT":
                return qs

        return qs.none()

    def has_change_permission(self, request, obj=None):
        user = request.user

        if hasattr(user, "role"):
            if user.role == "TENANT":
                return False
            if user.role == "LANDLORD":
                if obj is None:
                    return True
                return obj.owner == user

        return False

    def has_delete_permission(self, request, obj=None):
        return self.has_change_permission(request, obj)

    def has_add_permission(self, request):
        user = request.user
        return user.is_superuser or (hasattr(user, "role") and user.role == "LANDLORD")

    def has_module_permission(self, request):
        return True

    def get_list_filter(self, request):
        return self.list_filter

    def average_rating(self, obj):
        avg = obj.reviews.aggregate(Avg("rating"))["rating__avg"]
        return round(avg, 1) if avg is not None else "—"

    average_rating.short_description = "⭐ Average score"
    average_rating.admin_order_field = "reviews__rating"

    def price_display(self, obj):
        return f"{obj.price} € / month"

    price_display.short_description = "Price"


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("id", "rent", "tenant", "check_in", "check_out", "colored_status")
    list_filter = ("status", "check_in", "rent__city")
    search_fields = ("rent__title", "tenant__email")
    actions = ["confirm_booking", "decline_booking", "cancel_booking"]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        user = request.user

        if user.is_superuser:
            return qs

        if getattr(user, "role", None) == UserRole.TENANT.name:
            return qs.filter(tenant=user)

        if getattr(user, "role", None) == UserRole.LANDLORD.name:
            return qs.filter(rent__owner=user)

        return qs.none()

    def get_actions(self, request):
        actions = super().get_actions(request)

        if getattr(request.user, "role", None) == UserRole.TENANT.name:
            actions.pop("confirm_booking", None)
            actions.pop("decline_booking", None)
        return actions

    def get_readonly_fields(self, request, obj=None):
        if getattr(request.user, "role", None) == UserRole.TENANT.name:
            return super().get_readonly_fields(request, obj) + ("status", "tenant")
        return super().get_readonly_fields(request, obj)

    def get_fields(self, request, obj=None):
        fields = ["rent", "tenant", "check_in", "check_out", "status"]
        if getattr(request.user, "role", None) == UserRole.TENANT.name:
            fields.remove("status")
        return fields

    def save_model(self, request, obj, form, change):
        if not change and not request.user.is_superuser:
            obj.tenant = request.user
            obj.status = Booking.Status.PENDING
        obj.full_clean()
        super().save_model(request, obj, form, change)

    def colored_status(self, obj):
        color = {
            "PENDING": "orange",
            "CONFIRMED": "green",
            "DECLINED": "red",
            "CANCELLED": "gray"
        }.get(obj.status, "black")
        return format_html('<b style="color: {};">{}</b>', color, obj.get_status_display())

    colored_status.short_description = "Статус"

    def log_change(self, request, obj, message):
        LogEntry.objects.log_action(
            user_id=request.user.pk,
            content_type_id=ContentType.objects.get_for_model(obj).pk,
            object_id=obj.pk,
            object_repr=force_str(obj),
            action_flag=CHANGE,
            change_message=message,
        )

    def confirm_booking(self, request, queryset):
        if getattr(request.user, "role", None) != UserRole.LANDLORD.name:
            self.message_user(
                request,
                "❌ Только арендодатель может подтверждать брони.",
                level=messages.ERROR
            )
            return

        count = 0
        for booking in queryset:
            if booking.status != Booking.Status.PENDING:
                continue
            if booking.rent.owner != request.user:
                continue
            booking.status = Booking.Status.CONFIRMED
            booking.save()
            self.log_change(request, booking, "✅ Бронирование подтверждено через admin-действие")
            count += 1

        self.message_user(request, f"✅ confirm {count} booking.", messages.SUCCESS)

    confirm_booking.short_description = "✅ Confirm booking."

    def decline_booking(self, request, queryset):
        if getattr(request.user, "role", None) != UserRole.LANDLORD.name:
            self.message_user(request, "❌ Только арендодатель может отклонить бронирования.", level=messages.ERROR)
            return

        count = 0
        for booking in queryset:
            if booking.status != Booking.Status.PENDING:
                continue
            if booking.rent.owner != request.user:
                continue
            booking.status = Booking.Status.DECLINED
            booking.save()
            self.log_change(request, booking, "❌ Бронирование отклонено через admin-действие")
            count += 1

        self.message_user(request, f"❌ Отклонено {count} бронирований.", messages.WARNING)

    decline_booking.short_description = "❌ Decline booking"

    def cancel_booking(self, request, queryset):
        count = 0
        for booking in queryset:
            if booking.tenant != request.user:
                continue
            if not booking.can_cancel():
                continue
            booking.status = Booking.Status.CANCELLED
            booking.save()
            self.log_change(request, booking, "🔁 Бронирование отменено через admin-действие")
            count += 1
        self.message_user(request, f"🔁 Отменено {count} бронирований.", messages.INFO)

    cancel_booking.short_description = "🔁 Cancel booking (before check-in)"