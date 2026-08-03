from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.db.models.deletion import ProtectedError
from django.test import TestCase
from django.urls import reverse

from statuses.models import Status


class StatusViewsTest(TestCase):
    def setUp(self):
        user_model = get_user_model()

        self.user = user_model.objects.create_user(
            username="john",
            password="password123",
        )
        self.status = Status.objects.create(
            name="РќРѕРІС‹Р№",
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
        self.assertContains(response, "РЎС‚Р°С‚СѓСЃС‹")
        self.assertContains(response, "РќРѕРІС‹Р№")
        self.assertContains(
            response,
            "РЎРѕР·РґР°С‚СЊ СЃС‚Р°С‚СѓСЃ",
        )
        self.assertContains(response, "Р�Р·РјРµРЅРёС‚СЊ")
        self.assertContains(response, "РЈРґР°Р»РёС‚СЊ")

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
        self.assertContains(response, "РЎРѕР·РґР°С‚СЊ")

    def test_status_create(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("status_create"),
            {
                "name": "Р’ СЂР°Р±РѕС‚Рµ",
            },
        )

        self.assertRedirects(
            response,
            reverse("statuses_index"),
        )
        self.assertTrue(
            Status.objects.filter(
                name="Р’ СЂР°Р±РѕС‚Рµ"
            ).exists()
        )
        self.assertIn(
            "РЎС‚Р°С‚СѓСЃ СѓСЃРїРµС€РЅРѕ СЃРѕР·РґР°РЅ",
            self.get_message_texts(response),
        )

    def test_duplicate_status_name(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("status_create"),
            {
                "name": "РќРѕРІС‹Р№",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "СѓР¶Рµ СЃСѓС‰РµСЃС‚РІСѓРµС‚",
        )
        self.assertEqual(
            Status.objects.filter(
                name="РќРѕРІС‹Р№"
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
                "name": "РќР° С‚РµСЃС‚РёСЂРѕРІР°РЅРёРё",
            },
        )

        self.assertRedirects(
            response,
            reverse("statuses_index"),
        )

        self.status.refresh_from_db()

        self.assertEqual(
            self.status.name,
            "РќР° С‚РµСЃС‚РёСЂРѕРІР°РЅРёРё",
        )
        self.assertIn(
            "РЎС‚Р°С‚СѓСЃ СѓСЃРїРµС€РЅРѕ РёР·РјРµРЅРµРЅ",
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
            "РЎС‚Р°С‚СѓСЃ СѓСЃРїРµС€РЅРѕ СѓРґР°Р»РµРЅ",
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
            "РќРµРІРѕР·РјРѕР¶РЅРѕ СѓРґР°Р»РёС‚СЊ СЃС‚Р°С‚СѓСЃ",
            self.get_message_texts(response),
        )
