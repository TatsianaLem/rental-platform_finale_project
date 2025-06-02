from django.contrib import admin
from applications.rent.models import Review, Booking



@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("id", "rent", "author", "rating", "short_comment", "created_date")
    list_filter = ("rating", "created_at")
    search_fields = ("rent__title", "author__email", "comment")
    readonly_fields = ("author", "created_at",)

    def short_comment(self, obj):
        return (obj.comment[:50] + "...") if len(obj.comment) > 50 else obj.comment

    short_comment.short_description = "Comment"

    def created_date(self, obj):
        return obj.created_at.date()

    created_date.short_description = "Created at"
    created_date.admin_order_field = "created_at"

    def has_change_permission(self, request, obj=None):
        user = request.user

        if request.user.is_superuser:
            return True

        if obj:
            return obj.author == request.user

        return True

    def has_delete_permission(self, request, obj=None):
        return self.has_change_permission(request, obj)

    def has_add_permission(self, request):
        return request.user.is_authenticated

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(author=request.user)

class ReviewInline(admin.TabularInline):
    model = Review
    extra = 0
    readonly_fields = ("author", "created_at")
    fields = ("rating", "comment", "created_at")
    can_delete = False

    def has_add_permission(self, request, obj=None):
        if not obj or not request.user.is_authenticated:
            return False

        is_tenant = request.user.role == "TENANT"
        has_booking = obj.bookings.filter(
            tenant=request.user,
            status=Booking.Status.CONFIRMED
        ).exists()
        already_reviewed = Review.objects.filter(
            rent=obj,
            author=request.user
        ).exists()

        return is_tenant and has_booking and not already_reviewed

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(author=request.user)




# @admin.register(Review)
# class ReviewAdmin(admin.ModelAdmin):
#     list_display = ("id", "rent", "author", "rating", "created_at")
#     readonly_fields = ("created_at",)
#     search_fields = ("rent__title", "author__email", "comment")
#     list_filter = ("rating", "created_at")
#
#     def get_queryset(self, request):
#         qs = super().get_queryset(request)
#         user = request.user
#
#         if user.is_superuser:
#             return qs
#
#         if hasattr(user, "role") and user.role == "TENANT":
#             return qs.filter(author=user)
#
#         return qs.none()
#
#     def has_add_permission(self, request):
#         return hasattr(request.user, "role") and request.user.role == "TENANT"
#
#     def has_change_permission(self, request, obj=None):
#         if request.user.is_superuser:
#             return True
#         return obj and obj.author == request.user
#
#     def has_delete_permission(self, request, obj=None):
#         return self.has_change_permission(request, obj)
#
#     def formfield_for_foreignkey(self, db_field, request, **kwargs):
#         if db_field.name == "rent" and hasattr(request.user, "role") and request.user.role == "TENANT":
#             from applications.rent.models import Booking
#             confirmed = Booking.Status.CONFIRMED
#             booked_rents = Booking.objects.filter(
#                 tenant=request.user,
#                 status=confirmed
#             ).values_list("rent_id", flat=True)
#             from applications.rent.models import Rent
#             kwargs["queryset"] = Rent.objects.filter(id__in=booked_rents)
#         return super().formfield_for_foreignkey(db_field, request, **kwargs)


