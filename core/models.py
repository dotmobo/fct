from django.db import models
from django.contrib.auth.models import User

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
    event_date = models.DateField(verbose_name = 'Date de l\'événement')
    description = models.CharField(max_length=255, blank=True, verbose_name = 'Description')
    creation_date = models.DateTimeField(auto_now_add=True, verbose_name = 'Date de création')
    added_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name = 'Ajouté par')

    class Meta:
        verbose_name = 'Événement'
    
    def __str__(self):
        return self.get_event_type_display() + ' du ' + str(self.event_date)


