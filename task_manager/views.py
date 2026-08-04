from django.conf import settings
from django.http import HttpResponseForbidden
from django.views.generic import TemplateView


class IndexView(TemplateView):
    template_name = "index.html"

def rollbar_test(request):
    expected_token = settings.ROLLBAR_TEST_TOKEN
    provided_token = request.GET.get("token")

    if (
        not expected_token
        or provided_token != expected_token
    ):
        return HttpResponseForbidden(
            "Forbidden"
        )

    raise RuntimeError(
        "Rollbar production test error"
    )
