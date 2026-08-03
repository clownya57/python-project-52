from django import forms

from tasks.models import Task


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = (
            "name",
            "description",
            "status",
            "executor",
            "labels",
        )
        labels = {
            "name": "Имя",
            "description": "Описание",
            "status": "Статус",
            "executor": "Исполнитель",
            "labels": "Метки",
        }
        widgets = {
            "description": forms.Textarea(
                attrs={
                    "rows": 5,
                }
            ),
        }
        error_messages = {
            "name": {
                "unique": (
                    "Задача с таким именем уже существует"
                ),
            },
        }
