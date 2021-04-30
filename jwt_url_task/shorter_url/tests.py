import secrets
import string

from django.contrib.messages import get_messages
from django.test import TestCase
from django.urls import reverse

from .constants import (
    CREATE_VIEW_URL,
    SITE_EXISTS_MESSAGE,
    SUCCESS_MESSAGE,
    REDIRECT_VIEW_URL,
)
from .models import ShortenUrl


class TestShortenUrlCreateViewPOST(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.test_url = "https://www.wp.pl/"
        cls.test_invalid_url = "INVALID-URL"

    def test_status_code(self):
        response = self.client.post(reverse(CREATE_VIEW_URL))
        self.assertEqual(response.status_code, 200)

    def test_create_new_shortcut_with_param(self):
        self.assertEqual(ShortenUrl.objects.count(), 0)
        response = self.client.post(
            reverse(CREATE_VIEW_URL), {"long_url": self.test_url}
        )
        messages = list(map(str, get_messages(response.wsgi_request)))
        self.assertEqual(ShortenUrl.objects.count(), 1)
        self.assertEqual(len(messages), 1)
        self.assertIn(SUCCESS_MESSAGE, messages.pop())

    def test_create_new_shortcut_without_param(self):
        self.assertEqual(ShortenUrl.objects.count(), 0)
        self.client.post(reverse(CREATE_VIEW_URL))
        self.assertEqual(ShortenUrl.objects.count(), 0)

    def test_create_new_shortcut_for_existing_url(self):
        ShortenUrl.objects.create(long_url=self.test_url, short_url="TEST")
        self.assertEqual(ShortenUrl.objects.count(), 1)
        response = self.client.post(
            reverse(CREATE_VIEW_URL), {"long_url": self.test_url}
        )
        messages = list(map(str, get_messages(response.wsgi_request)))
        self.assertIn(SITE_EXISTS_MESSAGE, messages.pop())
        self.assertEqual(ShortenUrl.objects.count(), 1)

    def test_create_new_shortcut_with_invalid_url(self):
        self.assertEqual(ShortenUrl.objects.count(), 0)
        self.client.post(reverse(CREATE_VIEW_URL), {"long_url": self.test_invalid_url})
        self.assertEqual(ShortenUrl.objects.count(), 0)


class TestShortenUrlCreateViewGET(TestCase):
    def setUp(self) -> None:
        self.response = self.client.get(reverse(CREATE_VIEW_URL))

    def test_status_code(self):
        self.assertEqual(self.response.status_code, 200)


class TestShorterUrlRedirectViewGET(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.test_url = "https://www.wp.pl/"
        cls.test_short_url = "TEST"

    def test_redirect_with_url_existing_in_db(self):
        ShortenUrl.objects.create(long_url=self.test_url, short_url=self.test_short_url)
        response = self.client.get(
            reverse(REDIRECT_VIEW_URL, kwargs={"short_url": self.test_short_url})
        )
        self.assertRedirects(response, self.test_url, fetch_redirect_response=False)

    def test_redirect_with_url_not_existing_in_db(self):
        response = self.client.get(
            reverse(REDIRECT_VIEW_URL, kwargs={"short_url": self.test_short_url})
        )
        self.assertEqual(response.status_code, 404)


class ShortenUrlModel(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.test_url = "https://www.wp.pl/"

    def test_create_new_shorten_url_object(self):
        self.assertEqual(ShortenUrl.objects.count(), 0)
        ShortenUrl.create_with_new_url(long_url=self.test_url)
        self.assertEqual(ShortenUrl.objects.count(), 1)

    def test_if_short_url_attr_is_unique_for_every_new_object(self):
        self.assertEqual(ShortenUrl.objects.count(), 0)
        test_urls = [self._create_test_url() for _ in range(10)]
        for url in test_urls:
            ShortenUrl.create_with_new_url(url)
        self.assertEqual(ShortenUrl.objects.count(), 10)
        unique_shorten_urls = set(
            ShortenUrl.objects.values_list("short_url", flat=True)
        )
        self.assertEqual(len(unique_shorten_urls), 10)

    def _create_test_url(self):
        return f"https://{''.join([secrets.choice(string.ascii_letters) for _ in range(5)])}.pl/"
