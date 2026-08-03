from django.contrib import messages
from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    UserPassesTestMixin,
)
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import (
    DetailView,
    ListView,
)
from django.views.generic.edit import (
    CreateView,
    DeleteView,
    UpdateView,
)

from tasks.forms import TaskForm
from tasks.models import Task


class TaskAuthorPermissionMixin(
    LoginRequiredMixin,
    UserPassesTestMixin,
):
    def test_func(self):
        task = self.get_object()

        return self.request.user == task.author

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()

        messages.error(
            self.request,
            "Задачу может удалить только ее автор",
        )

        return redirect("tasks_index")

class TaskListView(
    LoginRequiredMixin,
    ListView,
):
    model = Task
    template_name = "tasks/index.html"
    context_object_name = "tasks"

    def get_queryset(self):
        return Task.objects.select_related(
            "status",
            "author",
            "executor",
        ).prefetch_related("labels")

class TaskDetailView(
    LoginRequiredMixin,
    DetailView,
):
    model = Task
    template_name = "tasks/show.html"
    context_object_name = "task"

    def get_queryset(self):
        return Task.objects.select_related(
            "status",
            "author",
            "executor",
        ).prefetch_related("labels")

class TaskCreateView(
    LoginRequiredMixin,
    SuccessMessageMixin,
    CreateView,
):
    model = Task
    form_class = TaskForm
    template_name = "tasks/form.html"
    success_url = reverse_lazy("tasks_index")
    success_message = "Задача успешно создана"
    title = "Создать задачу"
    button_text = "Создать"

    def form_valid(self, form):
        form.instance.author = self.request.user

        return super().form_valid(form)

class TaskUpdateView(
    LoginRequiredMixin,
    SuccessMessageMixin,
    UpdateView,
):
    model = Task
    form_class = TaskForm
    template_name = "tasks/form.html"
    success_url = reverse_lazy("tasks_index")
    success_message = "Задача успешно изменена"
    title = "Изменение задачи"
    button_text = "Изменить"

class TaskDeleteView(
    TaskAuthorPermissionMixin,
    DeleteView,
):
    model = Task
    template_name = "tasks/delete.html"
    success_url = reverse_lazy("tasks_index")

    def form_valid(self, form):
        messages.success(
            self.request,
            "Задача успешно удалена",
        )

        return super().form_valid(form)
