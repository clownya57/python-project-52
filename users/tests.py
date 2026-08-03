from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from django.test import TestCase
from django.urls import reverse


class UserViewsTest(TestCase):
    fixtures = ["users.json"]

    def setUp(self):
        self.user = User.objects.get(pk=1)
        self.user.set_password("password123")
        self.user.save()

        self.other_user = User.objects.get(pk=2)
        self.other_user.set_password("password123")
        self.other_user.save()

    @staticmethod
    def get_message_texts(response):
        return [
            str(message)
            for message in get_messages(
                response.wsgi_request
            )
        ]

    def test_users_index_is_public(self):
        response = self.client.get(
            reverse("users_index")
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "john")
        self.assertContains(response, "jane")

    def test_user_registration_page(self):
        response = self.client.get(
            reverse("user_create")
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            'name="username"',
        )
        self.assertContains(
            response,
            'id="id_username"',
        )
        self.assertContains(
            response,
            "Зарегистрировать",
        )

    def test_user_registration(self):
        response = self.client.post(
            reverse("user_create"),
            {
                "first_name": "Alex",
                "last_name": "Brown",
                "username": "alex",
                "password1": "strong-password-123",
                "password2": "strong-password-123",
            },
        )

        self.assertRedirects(
            response,
            reverse("login"),
        )
        self.assertTrue(
            User.objects.filter(
                username="alex"
            ).exists()
        )
        self.assertIn(
            "Пользователь успешно зарегистрирован",
            self.get_message_texts(response),
        )

    def test_duplicate_username(self):
        response = self.client.post(
            reverse("user_create"),
            {
                "first_name": "John",
                "last_name": "Second",
                "username": "john",
                "password1": "strong-password-123",
                "password2": "strong-password-123",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "уже существует",
        )

    def test_user_can_update_self(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse(
                "user_update",
                args=[self.user.pk],
            ),
            {
                "first_name": "Changed",
                "last_name": "User",
                "username": "john",
            },
        )

        self.assertRedirects(
            response,
            reverse("users_index"),
        )

        self.user.refresh_from_db()

        self.assertEqual(
            self.user.first_name,
            "Changed",
        )
        self.assertIn(
            "Пользователь успешно изменен",
            self.get_message_texts(response),
        )

    def test_user_cannot_update_another_user(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse(
                "user_update",
                args=[self.other_user.pk],
            ),
            {
                "first_name": "Changed",
                "last_name": "User",
                "username": "jane",
            },
        )

        self.assertRedirects(
            response,
            reverse("users_index"),
        )

        self.other_user.refresh_from_db()

        self.assertEqual(
            self.other_user.first_name,
            "Jane",
        )
        self.assertIn(
            "У вас нет прав для изменения",
self.get_message_texts(response),
        )

    def test_user_can_delete_self(self):
        user_id = self.user.pk

        self.client.force_login(self.user)

        response = self.client.post(
            reverse(
                "user_delete",
                args=[user_id],
            )
        )

        self.assertRedirects(
            response,
            reverse("users_index"),
        )
        self.assertFalse(
            User.objects.filter(
                pk=user_id
            ).exists()
        )
        self.assertIn(
            "Пользователь успешно удален",
            self.get_message_texts(response),
        )

    def test_login(self):
        response = self.client.post(
            reverse("login"),
            {
                "username": "john",
                "password": "password123",
            },
        )

        self.assertRedirects(
            response,
            reverse("index"),
        )
        self.assertIn(
            "_auth_user_id",
            self.client.session,
        )
        self.assertIn(
            "Вы залогинены",
            self.get_message_texts(response),
        )

    def test_logout(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("logout")
        )

        self.assertRedirects(
            response,
            reverse("index"),
        )
        self.assertNotIn(
            "_auth_user_id",
            self.client.session,
        )
        self.assertIn(
            "Вы разлогинены",
            self.get_message_texts(response),
        )
