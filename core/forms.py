from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from core.models import Event

class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=50, required=True, help_text='Veuillez saisir votre prénom', label="Prénom")
    last_name = forms.CharField(max_length=50, required=True, help_text='Veuillez saisir votre nom', label="Nom")
    email = forms.EmailField(max_length=255, help_text="Veuillez saisir votre adresse mail", label="Email")

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2', )


class CreateEventForm(forms.ModelForm):

    class Meta:
        model = Event
        fields = ['event_date', 'description', 'added_by']
        widgets = {
            'added_by': forms.HiddenInput(),
            'event_date': forms.TextInput(attrs={'type': 'date'})
        }