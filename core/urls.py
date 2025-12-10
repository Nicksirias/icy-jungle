from django.urls import path
from . import views
import hashlib

TEAM_NICKNAME = "icy-jungle"
ABTEST_SLUG = hashlib.sha1(TEAM_NICKNAME.encode()).hexdigest()[:7]


urlpatterns = [
    path("", views.home, name="home"),
    path("signin/", views.signin, name="signin"),
    path("logout/", views.logout, name="logout"),
    path("host-event/", views.host_event, name="host_event"),
    path("rsvp-toggle/<str:event_id>/", views.rsvp_toggle, name="rsvp_toggle"),
    path(f"{ABTEST_SLUG}/", views.abtest, name="abtest"),  # <- public A/B endpoint
]
