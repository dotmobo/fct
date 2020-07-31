from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from datetime import date
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.conf import settings

def present_or_future_date(value):
    if value < date.today():
        raise ValidationError("La date ne peux pas être passée.")
    return value

class Event(models.Model):
    ENTRAINEMENT = 'ENTRAINEMENT'
    MATCH = 'MATCH'
    MARCHE_GOURMANDE = 'MARCHE_GOURMANDE'
    FETE_DE_LA_CERISE = 'FETE_DE_LA_CERISE'
    JOURNEE_TRAVAIL = 'JOURNEE_TRAVAIL'
    AUTRES = 'AUTRES'
    EVENT_TYPES = [
        (ENTRAINEMENT, 'Entrainement'),
        (MATCH, 'Match'),
        (MARCHE_GOURMANDE, 'Marche gourmande'),
        (FETE_DE_LA_CERISE, 'Fête de la cerise'),
        (JOURNEE_TRAVAIL, 'Journée travail'),
        (AUTRES, 'Autres'),
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
    is_selected = models.BooleanField(null=True, verbose_name = 'Est sélectionné')

    class Meta:
        verbose_name = 'Présence'

    def __str__(self):
        return "%s - %s" % (self.event, self.attendee)

class Task(models.Model):
    BAR = 'BAR'
    EAU = 'EAU'
    LAVAGE_CHASUBLES = 'LAVAGE_CHASUBLES'
    VESTIAIRE = 'VESTIAIRE'
    TASK_ENTRAINEMENT = [LAVAGE_CHASUBLES, VESTIAIRE, EAU, BAR]
    TASK_TYPES = [
        (BAR, 'Bar'),
        (EAU, 'Eau'),
        (LAVAGE_CHASUBLES, 'Lavage chasubles'),
        (VESTIAIRE, 'Vestiaire'),
    ]

    attendance = models.OneToOneField(Attendance, on_delete=models.CASCADE, verbose_name = 'Présence')
    task_type = models.CharField(
        null=True,
        max_length=50,
        choices=TASK_TYPES,
        default=None,
        verbose_name = 'Type'
    )

    class Meta:
        verbose_name = 'Tâche'

    def __str__(self):
        return "%s - %s" % (self.attendance, self.task_type)

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email_confirmed = models.BooleanField(default=False)
    phone = models.CharField(max_length=20, blank=True, verbose_name="Téléphone")

@receiver(post_save, sender=User)
def update_user_profile(sender, instance, created, **kwargs):
    if created:
        if hasattr(instance, 'phone'):
            Profile.objects.create(user=instance, phone=instance.phone)
        else:
            Profile.objects.create(user=instance, phone='')
    instance.profile.save()


@receiver(post_save, sender=Attendance)
def send_event_mail(sender, instance, created, **kwargs):
    if created:
        subject = 'Valider votre présence'
        message = render_to_string('emails/attendance_validation.html', {
            'attendance': instance,
            'domain': settings.EMAIL_DOMAIN_LINK,
        })
        instance.attendee.email_user(subject, message)
    else:
        if instance.event.event_type == 'MATCH' and instance.is_attending == True and instance.is_selected == True:
            subject = 'Vous avez été sélectionné pour un match'
            message = render_to_string('emails/player_selection.html', {
                'attendance': instance,
                'domain': settings.EMAIL_DOMAIN_LINK,
            })
            instance.attendee.email_user(subject, message)

@receiver(post_save, sender=Task)
def send_task_mail(sender, instance, created, **kwargs):
    if created:
        subject = 'Une tâche vous a été affectée'
        message = render_to_string('emails/task_assignation.html', {
            'task': instance,
            'domain': settings.EMAIL_DOMAIN_LINK,
        })
        instance.attendance.attendee.email_user(subject, message)
