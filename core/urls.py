from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("signin/", views.signin, name="signin"),
    path("logout/", views.logout, name="logout"),
    path("host-event/", views.host_event, name="host_event"),
    path("rsvp-toggle/<str:event_id>/", views.rsvp_toggle, name="rsvp_toggle"),
]
