from enum import Enum


class UserRole(str, Enum):
    TENANT = "tenant"
    LANDLORD = "landlord"
    ADMIN = "admin"

    @classmethod
    def choices(cls):
        return [(key.name, key.value) for key in cls]
