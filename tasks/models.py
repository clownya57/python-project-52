from django.conf import settings
from django.db import models

from labels.models import Label
from statuses.models import Status


class Task(models.Model):
    name = models.CharField(
        max_length=150,
        unique=True,
        verbose_name="Имя",
    )
    description = models.TextField(
        blank=True,
        verbose_name="Описание",
    )
    status = models.ForeignKey(
        Status,
        on_delete=models.PROTECT,
        related_name="tasks",
        verbose_name="Статус",
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="authored_tasks",
        verbose_name="Автор",
    )
    executor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="assigned_tasks",
        null=True,
        blank=True,
        verbose_name="Исполнитель",
    )
    labels = models.ManyToManyField(
        Label,
        related_name="tasks",
        blank=True,
        verbose_name="Метки",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ["id"]
        verbose_name = "задача"
        verbose_name_plural = "задачи"

    def __str__(self):
        return self.name
