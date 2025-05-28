from django.db import models
from django.conf import settings
from applications.rent.models import Rent
from django.core.exceptions import ValidationError

class Review(models.Model):
    rent = models.ForeignKey(Rent, related_name="reviews", on_delete=models.CASCADE)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField()
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        unique_together = ("rent", "author")
        verbose_name = "Review"
        verbose_name_plural = "Reviews"

    def clean(self):
        if Review.objects.filter(rent=self.rent, author=self.author).exclude(pk=self.pk).exists():
            raise ValidationError("⛔ Вы уже оставляли отзыв к этому объявлению.")

    def __str__(self):
        return f"{self.author} - {self.rent} ({self.rating})"
