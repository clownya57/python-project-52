from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models.deletion import ProtectedError
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import ListView
from django.views.generic.edit import (
    CreateView,
    DeleteView,
    UpdateView,
)

from statuses.forms import StatusForm
from statuses.models import Status


class StatusListView(
    LoginRequiredMixin,
    ListView,
):
    model = Status
    template_name = "statuses/index.html"
    context_object_name = "statuses"

class StatusCreateView(
    LoginRequiredMixin,
    SuccessMessageMixin,
    CreateView,
):
    model = Status
    form_class = StatusForm
    template_name = "statuses/form.html"
    success_url = reverse_lazy("statuses_index")
    success_message = "Статус успешно создан"
    title = "Создать статус"
    button_text = "Создать"

class StatusUpdateView(
    LoginRequiredMixin,
    SuccessMessageMixin,
    UpdateView,
):
    model = Status
    form_class = StatusForm
    template_name = "statuses/form.html"
    success_url = reverse_lazy("statuses_index")
    success_message = "Статус успешно изменен"
    title = "Изменение статуса"
    button_text = "Изменить"

class StatusDeleteView(
    LoginRequiredMixin,
    DeleteView,
):
    model = Status
    template_name = "statuses/delete.html"
    success_url = reverse_lazy("statuses_index")

    def form_valid(self, form):
        try:
            response = super().form_valid(form)
        except ProtectedError:
            messages.error(
                self.request,
                "Невозможно удалить статус",
            )

            return redirect("statuses_index")

        messages.success(
            self.request,
            "Статус успешно удален",
        )

        return response

