from django.contrib import admin

from .models import Event

class EventAdmin(admin.ModelAdmin):
    list_display = ('event_type', 'event_date', 'description')
    list_filter = ('event_type',)

admin.site.register(Event, EventAdmin)