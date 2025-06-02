from django.contrib import admin, messages
from django.contrib.admin.models import LogEntry, CHANGE
from django.urls import reverse
from django.utils.html import format_html
from django.utils.encoding import force_str
from django.contrib.contenttypes.models import ContentType
from applications.rent.models import Booking
from applications.user.choices.roles import UserRole




@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("id", "rent", "tenant", "check_in", "check_out", "colored_status", "view_rent_link")
    list_filter = ("status", "check_in", "rent__city")
    search_fields = ("rent__title", "tenant__email")
    actions = ["confirm_booking", "decline_booking", "cancel_booking"]
    # inlines = [ReviewInline]

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

    def view_rent_link(self, obj):
        url = reverse("admin:rent_rent_change", args=[obj.rent.id])
        return format_html('<a href="{}">📄 Перейти к объявлению</a>', url)

    view_rent_link.short_description = "Объявление"