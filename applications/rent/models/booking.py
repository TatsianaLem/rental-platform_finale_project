from django.db import models
from django.conf import settings
from django.utils import timezone


class Booking(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Ожидает подтверждения"
        CONFIRMED = "CONFIRMED", "Подтверждено"
        DECLINED = "DECLINED", "Отклонено"
        CANCELLED = "CANCELLED", "Отменено"

    rent = models.ForeignKey("rent.Rent", on_delete=models.CASCADE, related_name="bookings")
    tenant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="bookings")
    check_in = models.DateField()
    check_out = models.DateField()
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

    def can_cancel(self):
        return timezone.now().date() < self.check_in - timezone.timedelta(days=1)

    def __str__(self):
        return f"{self.tenant} → {self.rent} ({self.check_in} to {self.check_out})"
