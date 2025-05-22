import django_filters
from applications.rent.models import Rent

class RentFilter(django_filters.FilterSet):
    min_price = django_filters.NumberFilter(field_name="price", lookup_expr="gte")
    max_price = django_filters.NumberFilter(field_name="price", lookup_expr="lte")
    min_rooms = django_filters.NumberFilter(field_name="rooms_count", lookup_expr="gte")
    max_rooms = django_filters.NumberFilter(field_name="rooms_count", lookup_expr="lte")
    address = django_filters.CharFilter(lookup_expr="icontains")
    room_type = django_filters.CharFilter()

    class Meta:
        model = Rent
        fields = []
