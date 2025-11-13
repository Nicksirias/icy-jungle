from django.db import models
from django.utils import timezone

# Create your models here.

class Event(models.Model):
    """Represents an event that users can host and others can RSVP to."""
    name = models.CharField(max_length=200, help_text="Name of the event")
    location = models.CharField(max_length=300, help_text="Location of the event")
    datetime = models.DateTimeField(help_text="Date and time of the event")
    details = models.TextField(help_text="Additional details about the event", blank=True)
    host_user_id = models.CharField(max_length=255, help_text="Supabase user ID of the event host")
    host_email = models.EmailField(help_text="Email of the event host")
    created_at = models.DateTimeField(default=timezone.now, help_text="When the event was created")
    
    class Meta:
        ordering = ['datetime']
    
    def __str__(self):
        return f"{self.name} - {self.datetime.strftime('%Y-%m-%d %H:%M')}"


class RSVP(models.Model):
    """Tracks which users have RSVP'd to which events."""
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='rsvps')
    user_id = models.CharField(max_length=255, help_text="Supabase user ID of the user who RSVP'd")
    user_email = models.EmailField(help_text="Email of the user who RSVP'd")
    created_at = models.DateTimeField(default=timezone.now, help_text="When the RSVP was created")
    
    class Meta:
        unique_together = ['event', 'user_id']  # Prevent duplicate RSVPs
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user_email} RSVP'd to {self.event.name}"
