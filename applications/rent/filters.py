import django_filters
from django.contrib import admin
from applications.rent.models import Rent

class RentFilter(django_filters.FilterSet):
    min_price = django_filters.NumberFilter(field_name="price", lookup_expr="gte")
    max_price = django_filters.NumberFilter(field_name="price", lookup_expr="lte")
    min_rooms = django_filters.NumberFilter(field_name="rooms_count", lookup_expr="gte")
    max_rooms = django_filters.NumberFilter(field_name="rooms_count", lookup_expr="lte")
    address = django_filters.CharFilter(lookup_expr="icontains")
    room_type = django_filters.CharFilter()
    city = django_filters.CharFilter(field_name="city", lookup_expr="iexact")

    class Meta:
        model = Rent
        fields = ["city", "room_type", "rooms_count"]


class CityListFilter(admin.SimpleListFilter):
    title = "City"
    parameter_name = "city"
    template = "admin/filters/dropdown_filter.html"

    def lookups(self, request, model_admin):
        cities = Rent.objects.values_list("city", flat=True).distinct()
        return [(city, city) for city in sorted(set(cities)) if city]

    def queryset(self, request, queryset):
        value = self.value()
        if value:
            return queryset.filter(city__iexact=value)
        return queryset

class PriceRangeDropdownFilter(admin.SimpleListFilter):
    title = "Price Range"
    parameter_name = "price_range"

    def lookups(self, request, model_admin):
        return [
            ("0-100", "до 100 €"),
            ("100-300", "100–300 €"),
            ("300-600", "300–600 €"),
            ("600-1000", "600–1000 €"),
            ("1000-2000", "1000–2000 €"),
            ("2000+", "более 2000 €"),
        ]

    def queryset(self, request, queryset):
        value = self.value()
        if value == "0-100":
            return queryset.filter(price__lte=100)
        elif value == "100-300":
            return queryset.filter(price__gt=100, price__lte=300)
        elif value == "300-600":
            return queryset.filter(price__gt=300, price__lte=600)
        elif value == "600-1000":
            return queryset.filter(price__gt=600, price__lte=1000)
        elif value == "1000-2000":
            return queryset.filter(price__gt=1000, price__lte=2000)
        elif value == "2000+":
            return queryset.filter(price__gt=2000)
        return queryset

class RoomsCountFilter(admin.SimpleListFilter):
    title = "Rooms"
    parameter_name = "rooms_count"

    def lookups(self, request, model_admin):
        counts = Rent.objects.values_list("rooms_count", flat=True).distinct()
        unique_counts = sorted(set(counts))
        return [(str(count), f"{count} room(s)") for count in unique_counts]

    def queryset(self, request, queryset):
        value = self.value()
        if value:
            return queryset.filter(rooms_count=value)
        return queryset


class RoomTypeFilter(admin.SimpleListFilter):
    title = "Room Type"
    parameter_name = "room_type"

    def lookups(self, request, model_admin):
        types = Rent.objects.values_list("room_type", flat=True).distinct()
        return [(room_type, room_type) for room_type in sorted(set(types)) if room_type]

    def queryset(self, request, queryset):
        value = self.value()
        if value:
            return queryset.filter(room_type=value)
        return queryset
