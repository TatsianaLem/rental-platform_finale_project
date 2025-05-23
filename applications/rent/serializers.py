from rest_framework import serializers
from applications.rent.models import Rent, Booking
from django.utils import timezone
from applications.rent.choices.room_type import RoomType
from django.db.models import Q



class RentSerializer(serializers.ModelSerializer):
    room_type_display = serializers.SerializerMethodField(read_only=True)
    price_display = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Rent
        fields = [
            "id",
            "owner",
            "title",
            "description",
            "city",
            "address",
            "latitude",
            "longitude",
            "price",
            "price_display",
            "rooms_count",
            "room_type",
            "room_type_display",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "owner", "created_at", "updated_at"]

    def get_room_type_display(self, obj):
        return RoomType[obj.room_type].value if obj.room_type else None

    def get_price_display(self, obj):
        return f"{obj.price} € / month"

    def create(self, validated_data):
        user = self.context["request"].user
        validated_data["owner"] = user
        return super().create(validated_data)

class BookingSerializer(serializers.ModelSerializer):
    status = serializers.CharField(read_only=True)

    class Meta:
        model = Booking
        fields = [
            "id", "rent", "tenant", "check_in", "check_out", "status", "created_at"
        ]
        read_only_fields = ["id", "tenant", "status", "created_at"]

    def validate(self, attrs):
        rent = attrs.get("rent")
        check_in = attrs.get("check_in")
        check_out = attrs.get("check_out")

        if check_in >= check_out:
            raise serializers.ValidationError("Check-out date must be later than check-in date.")

        overlapping = Booking.objects.filter(
            rent=rent,
            status__in=["PENDING", "CONFIRMED"],
            check_in__lt=check_out,
            check_out__gt=check_in
        ).exists()

        if overlapping:
            raise serializers.ValidationError("These dates are already busy.")

        return attrs

