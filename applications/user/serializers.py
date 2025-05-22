from rest_framework import serializers
from applications.user.models import User

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["email", "password", "first_name", "last_name", "phone", "role"]

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)
