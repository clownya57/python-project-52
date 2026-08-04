from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from labels.models import Label
from statuses.models import Status
from tasks.models import Task


class TaskFilterTest(TestCase):
    def setUp(self):
        user_model = get_user_model()

        self.user = user_model.objects.create_user(
            username="current_user",
            password="password123",
        )
        self.other_user = user_model.objects.create_user(
            username="other_user",
            password="password123",
        )

        self.new_status = Status.objects.create(
            name="new",
        )
        self.done_status = Status.objects.create(
            name="done",
        )

        self.bug_label = Label.objects.create(
            name="bug",
        )
        self.feature_label = Label.objects.create(
            name="feature",
        )

        self.own_task = Task.objects.create(
            name="own task",
            description="",
            status=self.new_status,
            author=self.user,
            executor=self.other_user,
        )
        self.own_task.labels.add(self.bug_label)

        self.assigned_task = Task.objects.create(
            name="assigned task",
            description="",
            status=self.done_status,
            author=self.other_user,
            executor=self.user,
        )
        self.assigned_task.labels.add(
            self.feature_label,
        )

        self.other_task = Task.objects.create(
            name="other task",
            description="",
            status=self.new_status,
            author=self.other_user,
            executor=None,
        )
        self.other_task.labels.add(
            self.bug_label,
            self.feature_label,
        )

        self.client.force_login(self.user)

    def get_response(self, params=None):
        return self.client.get(
            reverse("tasks_index"),
            params or {},
        )

    @staticmethod
    def get_task_ids(response):
        return set(
            response.context["tasks"].values_list(
                "id",
                flat=True,
            )
        )

    def test_filter_form_fields(self):
        response = self.get_response()
        form = response.context["filter"].form

        self.assertEqual(
            list(form.fields),
            [
                "status",
                "executor",
                "labels",
                "self_tasks",
            ],
        )

        expected_labels = {
            "status": (
                "\u0421\u0442\u0430\u0442\u0443\u0441"
            ),
            "executor": (
                "\u0418\u0441\u043f\u043e\u043b"
                "\u043d\u0438\u0442\u0435\u043b\u044c"
            ),
            "labels": (
                "\u041c\u0435\u0442\u043a\u0430"
            ),
            "self_tasks": (
                "\u0422\u043e\u043b\u044c\u043a\u043e "
                "\u0441\u0432\u043e\u0438 "
                "\u0437\u0430\u0434\u0430\u0447\u0438"
            ),
        }

        for field_name, expected_label in (
            expected_labels.items()
        ):
            with self.subTest(field_name=field_name):
                self.assertEqual(
                    form.fields[field_name].label,
                    expected_label,
                )

        self.assertEqual(
            form.fields["self_tasks"].widget.input_type,
            "checkbox",
        )

    def test_without_filters_returns_all_tasks(self):
        response = self.get_response()

        self.assertEqual(
            self.get_task_ids(response),
            {
                self.own_task.pk,
                self.assigned_task.pk,
                self.other_task.pk,
            },
        )

    def test_filter_by_status(self):
        response = self.get_response(
            {
                "status": self.new_status.pk,
            }
        )

        self.assertEqual(
            self.get_task_ids(response),
            {
                self.own_task.pk,
                self.other_task.pk,
            },
        )

    def test_filter_by_executor(self):
        response = self.get_response(
            {
                "executor": self.user.pk,
            }
        )

        self.assertEqual(
            self.get_task_ids(response),
            {
                self.assigned_task.pk,
            },
        )

    def test_filter_by_label(self):
        response = self.get_response(
            {
                "labels": self.bug_label.pk,
            }
        )

        self.assertEqual(
            self.get_task_ids(response),
            {
                self.own_task.pk,
                self.other_task.pk,
            },
        )

    def test_filter_only_own_tasks(self):
        response = self.get_response(
            {
                "self_tasks": "on",
            }
        )

        self.assertEqual(
            self.get_task_ids(response),
            {
                self.own_task.pk,
            },
        )

    def test_filters_can_be_combined(self):
        response = self.get_response(
            {
                "status": self.new_status.pk,
                "executor": self.other_user.pk,
                "labels": self.bug_label.pk,
                "self_tasks": "on",
            }
        )

        self.assertEqual(
            self.get_task_ids(response),
            {
                self.own_task.pk,
            },
        )
