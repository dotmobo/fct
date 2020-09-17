from django.http import HttpResponse
from django.shortcuts import render, render, redirect
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from datetime import date
from core.forms import SignUpForm, CreateEventForm, ModifyAttendanceForm, ModifySelectionForm
from core.decorators import group_required
from core.models import Event, Attendance, Task
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.template.loader import render_to_string
from core.tokens import account_activation_token
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.models import Group
from django.conf import settings
from django.db.models import Count
import random

def index(request):
    return render(request, 'index.html')

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            subject = 'Activez votre compte FCT'
            message = render_to_string('emails/account_activation_email.html', {
                'user': user,
                'domain': settings.EMAIL_DOMAIN_LINK,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            user.email_user(subject, message)
            return redirect('account_activation_sent')
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})

def signout(request):
    logout(request)
    return redirect('index')

def signin(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            next_url = request.GET.get('next')
            if next_url:
                return HttpResponseRedirect(next_url)
            else:
                return redirect('index')
    else:
        form = AuthenticationForm()
    return render(request, 'signin.html', {'form': form})

def account_activation_sent(request):
    return render(request, 'emails/account_activation_sent.html')

def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.profile.email_confirmed = True
        user.save()
        # Don't add the user to the group 'joueur' automatically
        # joueur = Group.objects.get(name='joueur')
        # joueur.user_set.add(user)
        login(request, user)
        return redirect('index')
    else:
        return render(request, 'emails/account_activation_invalid.html')

@group_required("entraineur", "comité")
def create_event(request):
    if request.method == 'POST':
        form = CreateEventForm(request.POST)
        if form.is_valid():
            new_event = form.save()
            form.cleaned_data['added_by'] = request.user
            # Create attendance for all players
            for u in User.objects.filter(groups__name__in=('joueur', 'entraineur', 'comité')).distinct():
                Attendance.objects.create(event=new_event, attendee=u, is_attending=None)
            return redirect('list_events')
    else:
        form = CreateEventForm(initial={'added_by': request.user})
    return render(request, 'events/create.html', {'form': form})

@group_required("entraineur", "joueur", "comité")
def list_events(request):
    return render(request, 'events/list.html', {'events': Event.objects.filter(event_date__gte=date.today())})

@group_required("entraineur", "joueur", "comité")
def list_attendances(request, event_id):
    return render(request, 'events/list_attendances.html',
        {'event': Event.objects.get(pk=event_id)})

@group_required("entraineur", "joueur", "comité")
def my_attendances(request):
    return render(request, 'events/my_attendances.html', {'attendances': Attendance.objects.filter(
        event__event_date__gte=date.today(), attendee=request.user)})


@group_required("entraineur", "joueur", "comité")
def my_attendance(request, attendance_id):
    attendance = Attendance.objects.get(pk=attendance_id)
    if attendance.attendee == request.user:
        if request.method == 'POST':
            form = ModifyAttendanceForm(request.POST, instance=attendance)
            if form.is_valid():
                form.save()
                return redirect('my_attendances')
        else:
            form = ModifyAttendanceForm(instance=attendance)
    else:
        return HttpResponseForbidden()
    return render(request, 'events/my_attendance.html', {'attendance': attendance, 'form': form})

@group_required("entraineur")
def player_selection(request, attendance_id):
    attendance = Attendance.objects.get(pk=attendance_id)
    if request.method == 'POST':
        form = ModifySelectionForm(request.POST, instance=attendance)
        if form.is_valid():
            form.save()
            return redirect('list_attendances', event_id=attendance.event.pk)
    else:
        form = ModifySelectionForm(instance=attendance)
    return render(request, 'events/player_selection.html', {'attendance': attendance, 'form': form})

@group_required("entraineur", "joueur", "comité")
def list_users(request):
    return render(request, 'users/list.html',
        {'users': User.objects.filter(is_active=True)})

@group_required("entraineur")
def assign_tasks(request, event_id):
    if request.method == 'POST':
        # Remove old tasks
        Task.objects.filter(attendance__event__pk=event_id).delete()
        event = Event.objects.get(pk=event_id)
        # entrainement tasks
        if event.event_type == Event.ENTRAINEMENT or event.event_type == Event.MATCH:
            # on récupères les présences et on les tri en fonction du nombres de tâches
            # des joueurs, pour éviter que çe soit toujours les mêmes qui fassent les tâches
            players = Attendance.objects.filter(
                event__pk=event_id,
                is_attending=True,
                attendee__groups__name__in=('joueur', )
            )
            # Pour les matchs on garde que les joueurs sélectionnées
            if event.event_type == Event.MATCH:
                players = players.filter(
                    is_selected=True
                )
            # On tri pour avoir les joueurs qui ont le moins de tâches
            players = players.annotate(count=Count('attendee__attending__task')).order_by('count')
            # On affecte les tâches
            if len(players) > 0:
                tasks_list = Task.TASK_ENTRAINEMENT if event.event_type == Event.ENTRAINEMENT else Task.TASK_MATCH
                random.shuffle(tasks_list)
                for num, task_type in enumerate(tasks_list, start=0):
                    if num < len(players):
                        Task.objects.create(attendance=players[num], task_type=task_type)
    return redirect('list_attendances', event_id=event_id)

@group_required("entraineur", "joueur", "comité")
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Le mot de passe a bien été changé!')
            return redirect('change_password')
        else:
            messages.error(request, 'Corrigez les erreurs ci-dessous.', extra_tags='danger')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'users/change_password.html', {
        'form': form
    })
