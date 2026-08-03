from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.test import TestCase
from django.urls import reverse

from labels.models import Label
from statuses.models import Status
from tasks.forms import TaskForm
from tasks.models import Task


class LabelViewsTest(TestCase):
    def setUp(self):
        user_model = get_user_model()

        self.user = user_model.objects.create_user(
            username="john",
            password="password123",
        )
        self.status = Status.objects.create(
            name="Новый",
        )
        self.label = Label.objects.create(
            name="Срочно",
        )
        self.linked_label = Label.objects.create(
            name="Баг",
        )
        self.task = Task.objects.create(
            name="Р�СЃРїСЂР°РІРёС‚СЊ РѕС€РёР±РєСѓ",
            description="Описание задачи",
            status=self.status,
            author=self.user,
        )
        self.task.labels.add(self.linked_label)

    @staticmethod
    def get_message_texts(response):
        return [
            str(message)
            for message in get_messages(
                response.wsgi_request
            )
        ]

    def test_label_pages_require_login(self):
        urls = [
            reverse("labels_index"),
            reverse("label_create"),
            reverse(
                "label_update",
                args=[self.label.pk],
            ),
            reverse(
                "label_delete",
                args=[self.label.pk],
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

    def test_labels_index(self):
        self.client.force_login(self.user)

        response = self.client.get(
            reverse("labels_index")
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Метки")
        self.assertContains(response, "Срочно")
        self.assertContains(response, "Баг")
        self.assertContains(
            response,
            "Создать метку",
        )
        self.assertContains(response, "Изменить")
        self.assertContains(response, "Удалить")

    def test_label_create_page_field_names(self):
        self.client.force_login(self.user)

        response = self.client.get(
            reverse("label_create")
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            'name="name"',
        )
        self.assertContains(
            response,
            'id="id_name"',
        )
        self.assertContains(response, "Создать")

    def test_label_create(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("label_create"),
            {
                "name": "Фича",
            },
        )

        self.assertRedirects(
            response,
            reverse("labels_index"),
        )
        self.assertTrue(
            Label.objects.filter(
                name="Фича"
            ).exists()
        )
        self.assertIn(
            "Метка успешно создана",
            self.get_message_texts(response),
        )

    def test_duplicate_label_name(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("label_create"),
            {
                "name": "Срочно",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "уже существует",
        )
        self.assertEqual(
            Label.objects.filter(
                name="Срочно"
            ).count(),
            1,
        )

    def test_label_update(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse(
                "label_update",
                args=[self.label.pk],
            ),
            {
                "name": "Важно",
            },
        )

        self.assertRedirects(
            response,
            reverse("labels_index"),
        )

        self.label.refresh_from_db()

        self.assertEqual(
            self.label.name,
            "Важно",
        )
        self.assertIn(
            "Метка успешно изменена",
            self.get_message_texts(response),
        )

    def test_unlinked_label_can_be_deleted(self):
        self.client.force_login(self.user)

        label_id = self.label.pk

        response = self.client.post(
            reverse(
                "label_delete",
                args=[label_id],
            )
        )

        self.assertRedirects(
            response,
            reverse("labels_index"),
        )
        self.assertFalse(
            Label.objects.filter(
                pk=label_id
            ).exists()
        )
        self.assertIn(
            "Метка успешно удалена",
            self.get_message_texts(response),
        )

    def test_linked_label_cannot_be_deleted(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse(
                "label_delete",
                args=[self.linked_label.pk],
            )
        )

        self.assertRedirects(
            response,
            reverse("labels_index"),
        )
        self.assertTrue(
            Label.objects.filter(
                pk=self.linked_label.pk
            ).exists()
        )
        self.assertTrue(
            self.task.labels.filter(
                pk=self.linked_label.pk
            ).exists()
        )
        self.assertIn(
            "Невозможно удалить метку",
            self.get_message_texts(response),
        )

    def test_task_form_supports_multiple_labels(self):
        field = TaskForm().fields["labels"]

        self.assertTrue(
            field.widget.allow_multiple_selected
        )

        self.client.force_login(self.user)

        urls = [
            reverse("task_create"),
            reverse(
                "task_update",
                args=[self.task.pk],
            ),
        ]

        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)

                self.assertEqual(
                    response.status_code,
                    200,
                )
                self.assertContains(
                    response,
                    'name="labels"',
                )
                self.assertContains(
                    response,
                    "multiple",
                )
