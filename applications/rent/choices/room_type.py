from enum import Enum


class RoomType(str, Enum):
    SINGLE_ROOM = "Single room (studio)"
    ONE_BEDROOM = "One room with separate bedroom"
    TWO_BEDROOM = "Two rooms with shared bathroom"
    TWO_BEDROOM_ENSUITE = "Two rooms with private bathrooms"
    THREE_BEDROOM = "Three rooms"
    SUITE = "Suite / Apartment"
    SHARED_ROOM = "Shared room / Bed space"
    PRIVATE_ROOM_IN_SHARED = "Private room in shared apartment"
    LOFT = "Loft / Attic"
    STUDIO = "Studio"

    @classmethod
    def choices(cls):
        return [(member.name, member.value) for member in cls]

    @classmethod
    def faker_choices(cls):
        return [member.name for member in cls]