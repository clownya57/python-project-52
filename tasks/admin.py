from django.contrib import admin

from tasks.models import Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "status",
        "author",
        "executor",
        "created_at",
    )
    list_filter = (
        "status",
        "labels",
    )
    search_fields = (
        "name",
        "description",
    )
    filter_horizontal = ("labels",)
