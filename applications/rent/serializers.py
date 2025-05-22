from rest_framework import serializers
from applications.rent.models import Rent
from applications.rent.choices.room_type import RoomType


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
            "address",
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

