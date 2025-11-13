from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("signin/", views.signin, name="signin"),
    path("logout/", views.logout, name="logout"),
    path("events/create/", views.create_event, name="create_event"),
    path("events/<int:event_id>/", views.event_detail, name="event_detail"),
    path("events/<int:event_id>/rsvp/", views.rsvp, name="rsvp"),
]
