from django.contrib import admin
from .models import Event

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'time', 'host_email', 'created_at')
    list_filter = ('time', 'created_at')
    search_fields = ('name', 'location', 'details')
