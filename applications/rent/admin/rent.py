from django.contrib import admin, messages
from django.db.models import Avg
from applications.rent.models import Rent
from applications.rent.admin.review import ReviewInline
from applications.rent.filters import (
    CityListFilter,
    RoomTypeFilter,
    RoomsCountFilter,
    PriceRangeDropdownFilter,
)



@admin.register(Rent)
class RentAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "owner", "city", "price_display",
        "rooms_count", "room_type", "is_active", "created_date", "average_rating",
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
        qs = qs.annotate(avg_rating=Avg("reviews__rating"))
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

        if user.is_superuser:
            return True

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
        #avg = obj.reviews.aggregate(Avg("rating"))["rating__avg"]
        avg = getattr(obj, "avg_rating", None)
        return round(avg, 1) if avg is not None else "—"

    average_rating.short_description = "⭐ Average score"
    average_rating.admin_order_field = "reviews__rating"

    def price_display(self, obj):
        return f"{obj.price} € / month"

    price_display.short_description = "Price"

    def created_date(self, obj):
        return obj.created_at.date()

    created_date.short_description = "Created at"
    created_date.admin_order_field = "created_at"
