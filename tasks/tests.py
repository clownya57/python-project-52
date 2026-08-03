from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.test import TestCase
from django.urls import reverse

from labels.models import Label
from statuses.models import Status
from tasks.models import Task


class TaskViewsTest(TestCase):
    def setUp(self):
        user_model = get_user_model()

        self.author = user_model.objects.create_user(
            username="author",
            password="password123",
            first_name="Task",
            last_name="Author",
        )
        self.other_user = user_model.objects.create_user(
            username="executor",
            password="password123",
            first_name="Task",
            last_name="Executor",
        )
        self.status = Status.objects.create(
            name="Новый",
        )
        self.label = Label.objects.create(
            name="Срочно",
        )
        self.task = Task.objects.create(
            name="Первая задача",
            description="Описание первой задачи",
            status=self.status,
            author=self.author,
            executor=self.other_user,
        )
        self.task.labels.add(self.label)

    @staticmethod
    def get_message_texts(response):
        return [
            str(message)
            for message in get_messages(
                response.wsgi_request
            )
        ]

    def test_task_pages_require_login(self):
        urls = [
            reverse("tasks_index"),
            reverse("task_create"),
            reverse(
                "task_show",
                args=[self.task.pk],
            ),
            reverse(
                "task_update",
                args=[self.task.pk],
            ),
            reverse(
                "task_delete",
                args=[self.task.pk],
            ),
        ]

        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)

                expected_url = (
                    f"{reverse('login')}?next={url}"
                )

                self.assertRedirects(
                    response,
                    expected_url,
                )

    def test_tasks_index_and_detail(self):
        self.client.force_login(self.author)

        index_response = self.client.get(
            reverse("tasks_index")
        )
        detail_response = self.client.get(
            reverse(
                "task_show",
                args=[self.task.pk],
            )
        )

        self.assertEqual(
            index_response.status_code,
            200,
        )
        self.assertContains(
            index_response,
            "Первая задача",
        )
        self.assertContains(
            index_response,
            "Показать",
        )
        self.assertContains(
            index_response,
            "Изменить",
        )
        self.assertContains(
            index_response,
            "Удалить",
        )

        self.assertEqual(
            detail_response.status_code,
            200,
        )
        self.assertContains(
            detail_response,
            "Описание первой задачи",
        )
        self.assertContains(
            detail_response,
            "Срочно",
        )
        self.assertContains(
            detail_response,
            "Метки",
        )

    def test_task_form_field_names(self):
        self.client.force_login(self.author)

        response = self.client.get(
            reverse("task_create")
        )

        self.assertEqual(response.status_code, 200)

        for field_name in (
            "name",
            "description",
            "status",
            "executor",
            "labels",
        ):
            with self.subTest(field_name=field_name):
                self.assertContains(
                    response,
                    f'name="{field_name}"',
                )

        self.assertContains(response, "Создать")

    def test_task_create_sets_author(self):
        self.client.force_login(self.author)

        response = self.client.post(
            reverse("task_create"),
            {
                "name": "Вторая задача",
                "description": "Новое описание",
                "status": self.status.pk,
                "executor": self.other_user.pk,
                "labels": [self.label.pk],
            },
        )

        self.assertRedirects(
            response,
            reverse("tasks_index"),
        )

        created_task = Task.objects.get(
            name="Вторая задача"
        )

        self.assertEqual(
            created_task.author,
            self.author,
        )
        self.assertEqual(
            created_task.executor,
            self.other_user,
        )
        self.assertTrue(
            created_task.labels.filter(
                pk=self.label.pk
            ).exists()
        )
        self.assertIn(
            "Задача успешно создана",
            self.get_message_texts(response),
        )

    def test_duplicate_task_name(self):
        self.client.force_login(self.author)

        response = self.client.post(
            reverse("task_create"),
            {
                "name": "Первая задача",
                "description": "Повтор",
                "status": self.status.pk,
                "executor": "",
                "labels": [],
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "уже существует",
        )
        self.assertEqual(
            Task.objects.filter(
                name="Первая задача"
            ).count(),
            1,
        )

    def test_logged_in_user_can_update_task(self):
        self.client.force_login(self.other_user)

        response = self.client.post(
            reverse(
                "task_update",
                args=[self.task.pk],
            ),
            {
                "name": "Р�Р·РјРµРЅС‘РЅРЅР°СЏ Р·Р°РґР°С‡Р°",
                "description": "Новое описание",
                "status": self.status.pk,
                "executor": self.author.pk,
                "labels": [self.label.pk],
            },
        )

        self.assertRedirects(
            response,
            reverse("tasks_index"),
        )

        self.task.refresh_from_db()

        self.assertEqual(
            self.task.name,
            "Р�Р·РјРµРЅС‘РЅРЅР°СЏ Р·Р°РґР°С‡Р°",
        )
        self.assertEqual(
            self.task.author,
            self.author,
        )
        self.assertEqual(
            self.task.executor,
            self.author,
        )
        self.assertIn(
            "Задача успешно изменена",
            self.get_message_texts(response),
        )

    def test_non_author_cannot_delete_task(self):
        self.client.force_login(self.other_user)

        response = self.client.post(
            reverse(
                "task_delete",
                args=[self.task.pk],
            )
        )

        self.assertRedirects(
            response,
            reverse("tasks_index"),
        )
        self.assertTrue(
            Task.objects.filter(
                pk=self.task.pk
            ).exists()
        )
        self.assertIn(
            "Задачу может удалить только ее автор",
            self.get_message_texts(response),
        )

    def test_author_can_delete_task(self):
        self.client.force_login(self.author)

        task_id = self.task.pk

        response = self.client.post(
            reverse(
                "task_delete",
                args=[task_id],
            )
        )

        self.assertRedirects(
            response,
            reverse("tasks_index"),
        )
        self.assertFalse(
            Task.objects.filter(
                pk=task_id
            ).exists()
        )
        self.assertIn(
            "Задача успешно удалена",
            self.get_message_texts(response),
        )

    def test_linked_status_cannot_be_deleted(self):
        self.client.force_login(self.author)

        response = self.client.post(
            reverse(
                "status_delete",
                args=[self.status.pk],
            )
        )

        self.assertRedirects(
            response,
            reverse("statuses_index"),
        )
        self.assertTrue(
            Status.objects.filter(
                pk=self.status.pk
            ).exists()
        )
        self.assertTrue(
            Task.objects.filter(
                pk=self.task.pk
            ).exists()
        )
        self.assertIn(
            "Невозможно удалить статус",
            self.get_message_texts(response),
        )

    def test_linked_user_cannot_be_deleted(self):
        self.client.force_login(self.author)

        response = self.client.post(
            reverse(
                "user_delete",
                args=[self.author.pk],
            )
        )

        self.assertRedirects(
            response,
            reverse("users_index"),
        )

        user_model = get_user_model()

        self.assertTrue(
            user_model.objects.filter(
                pk=self.author.pk
            ).exists()
        )
        self.assertTrue(
            Task.objects.filter(
                pk=self.task.pk
            ).exists()
        )
        self.assertIn(
            (
                "Невозможно удалить пользователя, "
                "потому что он используется"
            ),
            self.get_message_texts(response),
        )
