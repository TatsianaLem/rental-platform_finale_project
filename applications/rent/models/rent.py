from django.db import models
from django.conf import settings
from applications.rent.choices.room_type import RoomType
from django.utils.translation import gettext_lazy as _


class Rent(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="rents",
        verbose_name=_("Owner"),
    )
    title = models.CharField(_("Title"), max_length=100)
    description = models.TextField(_("Description"))
    address = models.CharField(_("Address"), max_length=170)
    price = models.DecimalField(_("Price"), max_digits=10, decimal_places=2)
    rooms_count = models.PositiveSmallIntegerField(_("Rooms count"))
    room_type = models.CharField(
        _("Room type"),
        max_length=45,
        choices=RoomType.choices()
    )
    is_active = models.BooleanField(_("Is active"), default=True)
    created_at = models.DateTimeField(_("Created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated at"), auto_now=True)

    class Meta:
        verbose_name = _("Announcement")
        verbose_name_plural = _("Announcements")
        ordering = ["-created_at"]
        db_table = "rent"

    def __str__(self):
        return f"{self.title} — {self.owner}"
