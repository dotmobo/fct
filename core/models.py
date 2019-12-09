from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from datetime import date
from django.db.models.signals import post_save
from django.dispatch import receiver

def present_or_future_date(value):
    if value < date.today():
        raise ValidationError("La date ne peux pas être passée.")
    return value

class Event(models.Model):
    ENTRAINEMENT = 'ENTRAINEMENT'
    MATCH = 'MATCH'
    EVENT_TYPES = [
        (ENTRAINEMENT, 'Entrainement'),
        (MATCH, 'Match'),
    ]

    event_type = models.CharField(
        max_length=50,
        choices=EVENT_TYPES,
        default=ENTRAINEMENT,
        verbose_name = 'Type'
    )
    event_date = models.DateField(verbose_name = 'Date de l\'événement', validators=[present_or_future_date])
    description = models.CharField(max_length=255, blank=True, verbose_name = 'Description')
    creation_date = models.DateTimeField(auto_now_add=True, verbose_name = 'Date de création')
    added_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name = 'Ajouté par')

    class Meta:
        verbose_name = 'Événement'
    
    def __str__(self):
        return self.get_event_type_display() + ' du ' + str(self.event_date)


class Attendance(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='attendants', verbose_name = 'Événement')
    attendee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='attending', verbose_name = 'Participant')
    is_attending = models.BooleanField(null=True, verbose_name = 'Est présent')

    class Meta:
        verbose_name = 'Présence'

    def __str__(self):
        return "%s - %s" % (self.event, self.attendee)

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email_confirmed = models.BooleanField(default=False)

@receiver(post_save, sender=User)
def update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()