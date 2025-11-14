from django.db import models
from django.contrib.auth.models import User

class Event(models.Model):
    name = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    time = models.DateTimeField()
    details = models.TextField(blank=True)
    host_email = models.EmailField()  # Store who created the event
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['time']  # Order by event time
    
    def __str__(self):
        return self.name
