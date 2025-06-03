from django.db.models import Avg
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from applications.rent.models import Rent, Booking
from applications.rent.models.review import Review
from applications.rent.choices.room_type import RoomType



class RentSerializer(serializers.ModelSerializer):
    room_type_display = serializers.SerializerMethodField(read_only=True)
    price_display = serializers.SerializerMethodField(read_only=True)
    average_rating = serializers.SerializerMethodField(read_only=True)

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
            "average_rating",
        ]
        read_only_fields = ["id", "owner", "created_at", "updated_at"]

    def get_room_type_display(self, obj):
        return RoomType[obj.room_type].value if obj.room_type else None

    def get_price_display(self, obj):
        return f"{obj.price} € / month"

    def get_average_rating(self, obj):
        avg = obj.reviews.aggregate(Avg("rating"))["rating__avg"]
        return round(avg, 1) if avg is not None else None

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

class ReviewSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source="author.__str__", read_only=True)

    class Meta:
        model = Review
        fields = ["id", "rent", "author_name", "rating", "comment", "created_at"]
        read_only_fields = ["author_name", "created_at"]

    def validate(self, data):
        user = self.context["request"].user
        rent = data.get("rent")
        rating = data.get("rating")

        review = Review(
            author=user,
            rent=rent,
            rating=rating,
            comment=data.get("comment", "")
        )

        try:
            review.clean()
        except ValidationError as e:
            raise ValidationError({"non_field_errors": e.detail if hasattr(e, 'detail') else e.args})

        return data

    def create(self, validated_data):
        validated_data["author"] = self.context["request"].user
        return super().create(validated_data)

        # if Review.objects.filter(rent=rent, author=user).exists():
        #     raise ValidationError("⛔ Вы уже оставляли отзыв на это объявление.")
        #
        # return data