from django.contrib.auth.models import Permission
from rest_framework import serializers
from applications.user.models import User

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["email", "password", "first_name", "last_name", "phone", "role"]

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)

        if user.role == "TENANT":
            tenant_permissions = [
                "view_rent", "add_booking", "view_booking",
                "delete_booking", "add_review", "view_review"
            ]
            for codename in tenant_permissions:
                try:
                    permission = Permission.objects.get(codename=codename)
                    user.user_permissions.add(permission)
                except Permission.DoesNotExist:
                    continue

        elif user.role == "LANDLORD":
            landlord_permissions = [
                "add_rent", "change_rent", "delete_rent", "view_rent",
                "view_booking", "change_booking"
            ]
            for codename in landlord_permissions:
                try:
                    permission = Permission.objects.get(codename=codename)
                    user.user_permissions.add(permission)
                except Permission.DoesNotExist:
                    continue

        return user