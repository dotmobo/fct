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
    )
    event_date = models.DateField()
    description = models.CharField(max_length=255)
    

