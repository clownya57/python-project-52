from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import ListView
from django.views.generic.edit import (
    CreateView,
    DeleteView,
    UpdateView,
)

from labels.forms import LabelForm
from labels.models import Label


class LabelListView(
    LoginRequiredMixin,
    ListView,
):
    model = Label
    template_name = "labels/index.html"
    context_object_name = "labels"

class LabelCreateView(
    LoginRequiredMixin,
    SuccessMessageMixin,
    CreateView,
):
    model = Label
    form_class = LabelForm
    template_name = "labels/form.html"
    success_url = reverse_lazy("labels_index")
    success_message = "Метка успешно создана"
    title = "Создать метку"
    button_text = "Создать"

class LabelUpdateView(
    LoginRequiredMixin,
    SuccessMessageMixin,
    UpdateView,
):
    model = Label
    form_class = LabelForm
    template_name = "labels/form.html"
    success_url = reverse_lazy("labels_index")
    success_message = "Метка успешно изменена"
    title = "Изменение метки"
    button_text = "Изменить"

class LabelDeleteView(
    LoginRequiredMixin,
    DeleteView,
):
    model = Label
    template_name = "labels/delete.html"
    success_url = reverse_lazy("labels_index")

    def form_valid(self, form):
        if self.object.tasks.exists():
            messages.error(
                self.request,
                "Невозможно удалить метку",
            )

            return redirect("labels_index")

        messages.success(
            self.request,
            "Метка успешно удалена",
        )

        return super().form_valid(form)
