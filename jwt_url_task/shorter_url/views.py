from typing import Union

from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.forms import Form
from django.http.response import HttpResponsePermanentRedirect
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.views.generic import RedirectView
from django.views.generic.edit import CreateView

from .constants import (
    CREATE_VIEW_URL,
    SITE_EXISTS_MESSAGE,
    SUCCESS_MESSAGE,
)
from .models import ShortenUrl


class ShortenUrlCreateView(CreateView, SuccessMessageMixin):
    model = ShortenUrl
    fields = ("long_url",)
    template_name = "shorter_url/create.html"

    def get_success_url(self):
        return self.request.path

    def form_valid(self, form: Form) -> HttpResponsePermanentRedirect:
        long_url = form.cleaned_data.get("long_url")
        new_shorter_url = ShortenUrl.create_with_new_url(long_url)
        self._send_success_message(SUCCESS_MESSAGE, long_url, new_shorter_url.short_url)
        return redirect(reverse(CREATE_VIEW_URL))

    def form_invalid(
        self, form: Form
    ) -> Union[HttpResponsePermanentRedirect, TemplateResponse]:
        long_url = form.data.get("long_url")
        if long_url and ShortenUrl.objects.filter(long_url=long_url).exists():
            shorten_url = ShortenUrl.objects.get(long_url=long_url)
            self._send_success_message(
                SITE_EXISTS_MESSAGE, long_url, shorten_url.short_url
            )
            return redirect(reverse(CREATE_VIEW_URL))
        return super(ShortenUrlCreateView, self).form_invalid(form)

    def _send_success_message(self, prefix: str, long_url: str, short_url: str) -> None:
        complete_short_url = f"{self.request.build_absolute_uri()}{short_url}"
        message = f"{prefix}. From {long_url} was created under {complete_short_url} shortcut."
        messages.success(self.request, message)


class ShorterUrlRedirectView(RedirectView):
    def get_redirect_url(self, *args, **kwargs) -> str:
        if short_url := kwargs.get("short_url"):
            shorten_url = get_object_or_404(ShortenUrl, short_url=short_url)
            return shorten_url.long_url
