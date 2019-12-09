from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from core.models import Event, Attendance

class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=50, required=True, help_text='Veuillez saisir votre prénom', label="Prénom")
    last_name = forms.CharField(max_length=50, required=True, help_text='Veuillez saisir votre nom', label="Nom")
    email = forms.EmailField(max_length=255, help_text="Veuillez saisir votre adresse mail", label="Email")

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2', )


class CreateEventForm(forms.ModelForm):
    disabled_fields = ('added_by', )

    def __init__(self, *args, **kwargs):
        super(CreateEventForm, self).__init__(*args, **kwargs)
        for field in self.disabled_fields:
            self.fields[field].disabled = True

    class Meta:
        model = Event
        fields = ['event_type', 'event_date', 'description', 'added_by']
        widgets = {
            'added_by': forms.HiddenInput(),
            'event_date': forms.TextInput(attrs={'type': 'date'})
        }

class ModifyAttendanceForm(forms.ModelForm):
    disabled_fields = ('event', 'attendee')

    def __init__(self, *args, **kwargs):
        super(ModifyAttendanceForm, self).__init__(*args, **kwargs)
        for field in self.disabled_fields:
            self.fields[field].disabled = True

    class Meta:
        model = Attendance
        fields = ['event', 'attendee', 'is_attending']
        widgets = {
            'event': forms.HiddenInput(),
            'attendee': forms.HiddenInput(),
        }
