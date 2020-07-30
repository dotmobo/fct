from django.contrib import admin

from .models import Event, Attendance, Profile

class EventAdmin(admin.ModelAdmin):
    list_display = ('event_type', 'event_date', 'description', 'added_by')
    list_filter = ('event_type',)

class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('event', 'attendee', 'is_attending', 'is_selected')
    list_filter = ('event', 'is_attending', 'is_selected')

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'email_confirmed', 'phone')
    list_filter = ('user', 'email_confirmed', 'phone')

admin.site.register(Event, EventAdmin)
admin.site.register(Attendance, AttendanceAdmin)
admin.site.register(Profile, ProfileAdmin)