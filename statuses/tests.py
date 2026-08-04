from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.db.models.deletion import ProtectedError
from django.test import TestCase
from django.urls import reverse

from statuses.models import Status

STATUS_NEW = "\u041d\u043e\u0432\u044b\u0439"
STATUS_IN_PROGRESS = (
    "\u0412 \u0440\u0430\u0431\u043e\u0442\u0435"
)
STATUS_TESTING = (
    "\u041d\u0430 "
    "\u0442\u0435\u0441\u0442\u0438\u0440\u043e\u0432\u0430\u043d\u0438\u0438"
)

TEXT_STATUSES = (
    "\u0421\u0442\u0430\u0442\u0443\u0441\u044b"
)
TEXT_CREATE_STATUS = (
    "\u0421\u043e\u0437\u0434\u0430\u0442\u044c "
    "\u0441\u0442\u0430\u0442\u0443\u0441"
)
TEXT_CREATE = (
    "\u0421\u043e\u0437\u0434\u0430\u0442\u044c"
)
TEXT_UPDATE = (
    "\u0418\u0437\u043c\u0435\u043d\u0438\u0442\u044c"
)
TEXT_DELETE = (
    "\u0423\u0434\u0430\u043b\u0438\u0442\u044c"
)
TEXT_ALREADY_EXISTS = (
    "\u0443\u0436\u0435 "
    "\u0441\u0443\u0449\u0435\u0441\u0442\u0432\u0443\u0435\u0442"
)

MESSAGE_CREATED = (
    "\u0421\u0442\u0430\u0442\u0443\u0441 "
    "\u0443\u0441\u043f\u0435\u0448\u043d\u043e "
    "\u0441\u043e\u0437\u0434\u0430\u043d"
)
MESSAGE_UPDATED = (
    "\u0421\u0442\u0430\u0442\u0443\u0441 "
    "\u0443\u0441\u043f\u0435\u0448\u043d\u043e "
    "\u0438\u0437\u043c\u0435\u043d\u0435\u043d"
)
MESSAGE_DELETED = (
    "\u0421\u0442\u0430\u0442\u0443\u0441 "
    "\u0443\u0441\u043f\u0435\u0448\u043d\u043e "
    "\u0443\u0434\u0430\u043b\u0435\u043d"
)
MESSAGE_PROTECTED = (
    "\u041d\u0435\u0432\u043e\u0437\u043c\u043e\u0436\u043d\u043e "
    "\u0443\u0434\u0430\u043b\u0438\u0442\u044c "
    "\u0441\u0442\u0430\u0442\u0443\u0441"
)


class StatusViewsTest(TestCase):
    def setUp(self):
        user_model = get_user_model()

        self.user = user_model.objects.create_user(
            username="john",
            password="password123",
        )
        self.status = Status.objects.create(
            name=STATUS_NEW,
        )

    @staticmethod
    def get_message_texts(response):
        return [
            str(message)
            for message in get_messages(
                response.wsgi_request
            )
        ]

    def test_status_pages_require_login(self):
        urls = [
            reverse("statuses_index"),
            reverse("status_create"),
            reverse(
                "status_update",
                args=[self.status.pk],
            ),
            reverse(
                "status_delete",
                args=[self.status.pk],
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

    def test_statuses_index(self):
        self.client.force_login(self.user)

        response = self.client.get(
            reverse("statuses_index")
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            TEXT_STATUSES,
        )
        self.assertContains(
            response,
            STATUS_NEW,
        )
        self.assertContains(
            response,
            TEXT_CREATE_STATUS,
        )
        self.assertContains(
            response,
            TEXT_UPDATE,
        )
        self.assertContains(
            response,
            TEXT_DELETE,
        )

    def test_status_create_page_field_names(self):
        self.client.force_login(self.user)

        response = self.client.get(
            reverse("status_create")
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
        self.assertContains(
            response,
            TEXT_CREATE,
        )

    def test_status_create(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("status_create"),
            {
                "name": STATUS_IN_PROGRESS,
            },
        )

        self.assertRedirects(
            response,
            reverse("statuses_index"),
        )
        self.assertTrue(
            Status.objects.filter(
                name=STATUS_IN_PROGRESS
            ).exists()
        )
        self.assertIn(
            MESSAGE_CREATED,
            self.get_message_texts(response),
        )

    def test_duplicate_status_name(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("status_create"),
            {
                "name": STATUS_NEW,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            TEXT_ALREADY_EXISTS,
        )
        self.assertEqual(
            Status.objects.filter(
                name=STATUS_NEW
            ).count(),
            1,
        )

    def test_status_update(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse(
                "status_update",
                args=[self.status.pk],
            ),
            {
                "name": STATUS_TESTING,
            },
        )

        self.assertRedirects(
            response,
            reverse("statuses_index"),
        )

        self.status.refresh_from_db()

        self.assertEqual(
            self.status.name,
            STATUS_TESTING,
        )
        self.assertIn(
            MESSAGE_UPDATED,
            self.get_message_texts(response),
        )

    def test_status_delete(self):
        self.client.force_login(self.user)

        status_id = self.status.pk

        response = self.client.post(
            reverse(
                "status_delete",
                args=[status_id],
            )
        )

        self.assertRedirects(
            response,
            reverse("statuses_index"),
        )
        self.assertFalse(
            Status.objects.filter(
                pk=status_id
            ).exists()
        )
        self.assertIn(
            MESSAGE_DELETED,
            self.get_message_texts(response),
        )

    def test_protected_status_cannot_be_deleted(self):
        self.client.force_login(self.user)

        protected_error = ProtectedError(
            "Status is protected",
            [self.status],
        )

        with patch(
            "statuses.models.Status.delete",
            side_effect=protected_error,
        ):
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
        self.assertIn(
            MESSAGE_PROTECTED,
            self.get_message_texts(response),
        )
