from django.db import models


class Label(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Имя",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ["id"]
        verbose_name = "метка"
        verbose_name_plural = "метки"

    def __str__(self):
        return self.name
