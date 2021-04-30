from django.db import models

from .utils import create_new_url


class ShortenUrl(models.Model):
    long_url = models.URLField(unique=True)
    short_url = models.CharField(unique=True, max_length=10)

    @classmethod
    def create_with_new_url(cls, long_url: str):
        new_url = create_new_url()
        while ShortenUrl.objects.filter(short_url__in=[new_url]).exists():
            new_url = create_new_url()
        return cls.objects.create(long_url=long_url, short_url=new_url)
