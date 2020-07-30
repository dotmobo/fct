from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from core.models import Event, Attendance

class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=50, required=True, help_text='Veuillez saisir votre prénom', label="Prénom")
    last_name = forms.CharField(max_length=50, required=True, help_text='Veuillez saisir votre nom', label="Nom")
    email = forms.EmailField(max_length=255, help_text="Veuillez saisir votre adresse mail", label="Email")
    phone = forms.CharField(max_length=20, help_text="Veuillez saisir votre numéro de téléphone", label="Téléphone")

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'phone', 'password1', 'password2', )

    def save(self, commit=True):
        user = super(SignUpForm, self).save(commit=False)
        user.phone = self.cleaned_data["phone"]
        if commit:
            user.save()
        return user


class CreateEventForm(forms.ModelForm):
    # TODO fix it disabled_fields = ('added_by', )

    # def __init__(self, *args, **kwargs):
    #    super(CreateEventForm, self).__init__(*args, **kwargs)
    #    for field in self.disabled_fields:
    #        self.fields[field].disabled = True

    class Meta:
        model = Event
        fields = ['event_type', 'event_date', 'description', 'added_by']
        widgets = {
            'added_by': forms.HiddenInput(),
            'event_date': forms.TextInput(attrs={'type': 'date'})
        }

class ModifyAttendanceForm(forms.ModelForm):
    disabled_fields = ('event', 'attendee', 'is_selected')

    def __init__(self, *args, **kwargs):
        super(ModifyAttendanceForm, self).__init__(*args, **kwargs)
        for field in self.disabled_fields:
            self.fields[field].disabled = True

    class Meta:
        model = Attendance
        fields = ['event', 'attendee', 'is_attending', 'is_selected']
        widgets = {
            'event': forms.HiddenInput(),
            'attendee': forms.HiddenInput(),
            'is_selected': forms.HiddenInput(),
        }

class ModifySelectionForm(forms.ModelForm):
    disabled_fields = ('event', 'attendee', 'is_attending')

    def __init__(self, *args, **kwargs):
        super(ModifySelectionForm, self).__init__(*args, **kwargs)
        for field in self.disabled_fields:
            self.fields[field].disabled = True

    class Meta:
        model = Attendance
        fields = ['event', 'attendee', 'is_attending', 'is_selected']
        widgets = {
            'event': forms.HiddenInput(),
            'attendee': forms.HiddenInput(),
            'is_attending': forms.HiddenInput(),
        }
