import django_filters
from django import forms
from django.contrib.auth import get_user_model

from labels.models import Label
from statuses.models import Status
from tasks.models import Task

user_model = get_user_model()

class TaskFilter(django_filters.FilterSet):
    status = django_filters.ModelChoiceFilter(
        field_name="status",
        queryset=Status.objects.all(),
        label="Статус",
    )
    executor = django_filters.ModelChoiceFilter(
        field_name="executor",
        queryset=user_model.objects.all(),
        label="Исполнитель",
    )
    labels = django_filters.ModelChoiceFilter(
        field_name="labels",
        queryset=Label.objects.all(),
        label="Метка",
        distinct=True,
    )
    self_tasks = django_filters.BooleanFilter(
        label="Только свои задачи",
        method="filter_self_tasks",
        widget=forms.CheckboxInput,
    )

    class Meta:
        model = Task
        fields = (
            "status",
            "executor",
            "labels",
        )

    def filter_self_tasks(
        self,
        queryset,
        _name,
        value,
    ):
        if value and self.request is not None:
            return queryset.filter(
                author=self.request.user,
            )

        return queryset
