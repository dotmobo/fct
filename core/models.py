from django.db import models

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
    event_date = models.DateField(verbose_name = 'Date')
    description = models.CharField(max_length=255, blank=True, verbose_name = 'Description')

    class Meta:
        verbose_name = 'Événement'
    
    def __str__(self):
        return self.get_event_type_display() + ' du ' + str(self.event_date)


