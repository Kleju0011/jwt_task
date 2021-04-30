from django.urls import path

from .views import ShortenUrlCreateView, ShorterUrlRedirectView

urlpatterns = [
    path("", ShortenUrlCreateView.as_view(), name="create"),
    path("<str:short_url>", ShorterUrlRedirectView.as_view(), name="redirect"),
]
