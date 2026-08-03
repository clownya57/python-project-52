from django.contrib import messages
from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    UserPassesTestMixin,
)
from django.contrib.auth.models import User
from django.contrib.auth.views import (
    LoginView,
    LogoutView,
)
from django.contrib.messages.views import (
    SuccessMessageMixin,
)
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import ListView
from django.views.generic.edit import (
    CreateView,
    DeleteView,
    UpdateView,
)

from users.forms import (
    UserCreateForm,
    UserLoginForm,
    UserUpdateForm,
)


class UserPermissionMixin(
    LoginRequiredMixin,
    UserPassesTestMixin,
):
    def test_func(self):
        edited_user = self.get_object()

        return self.request.user.pk == edited_user.pk

    def handle_no_permission(self):
        messages.error(
            self.request,
            "У вас нет прав для изменения",
        )

        return redirect("users_index")

class UserListView(ListView):
    model = User
    template_name = "users/index.html"
    context_object_name = "users"
    ordering = ["id"]

class UserCreateView(
    SuccessMessageMixin,
    CreateView,
):
    form_class = UserCreateForm
    template_name = "users/form.html"
    success_url = reverse_lazy("login")
    success_message = (
        "Пользователь успешно зарегистрирован"
    )
    title = "Регистрация"
    button_text = "Зарегистрировать"

class UserUpdateView(
    UserPermissionMixin,
    SuccessMessageMixin,
    UpdateView,
):
    model = User
    form_class = UserUpdateForm
    template_name = "users/form.html"
    success_url = reverse_lazy("users_index")
    success_message = (
        "Пользователь успешно изменен"
    )
    title = "Изменение пользователя"
    button_text = "Изменить"

class UserDeleteView(
    UserPermissionMixin,
    DeleteView,
):
    model = User
    template_name = "users/delete.html"
    success_url = reverse_lazy("users_index")

    def form_valid(self, form):
        messages.success(
            self.request,
            "Пользователь успешно удален",
        )

        return super().form_valid(form)

class UserLoginView(
    SuccessMessageMixin,
    LoginView,
):
    authentication_form = UserLoginForm
    template_name = "registration/login.html"
    next_page = reverse_lazy("index")
    success_message = "Вы залогинены"

class UserLogoutView(LogoutView):
    next_page = reverse_lazy("index")

    def post(self, request, *args, **kwargs):
        response = super().post(
            request,
            *args,
            **kwargs,
        )

        messages.success(
            request,
            "Вы разлогинены",
        )

        return response
