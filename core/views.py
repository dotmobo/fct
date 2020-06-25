from django.http import HttpResponse
from django.shortcuts import render, render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from datetime import date
from core.forms import SignUpForm, CreateEventForm, ModifyAttendanceForm
from core.decorators import group_required
from core.models import Event, Attendance
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.template.loader import render_to_string
from core.tokens import account_activation_token
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.models import Group
from django.conf import settings

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
        joueur = Group.objects.get(name='joueur') 
        joueur.user_set.add(user)    
        login(request, user)
        return redirect('index')
    else:
        return render(request, 'emails/account_activation_invalid.html')

@group_required("entraineur")
def create_event(request):
    if request.method == 'POST':
        form = CreateEventForm(request.POST)
        print(form.is_valid())
        if form.is_valid():
            new_event = form.save()
            form.cleaned_data['added_by'] = request.user
            # Create attendance for all players
            for u in User.objects.filter(groups__name__in=('joueur', 'entraineur') ):
                Attendance.objects.create(event=new_event, attendee=u, is_attending=None)
            return redirect('list_events')
    else:
        form = CreateEventForm(initial={'added_by': request.user})
    return render(request, 'events/create.html', {'form': form})

@group_required("entraineur", "joueur")
def list_events(request):
    return render(request, 'events/list.html', {'events': Event.objects.filter(event_date__gte=date.today())})

@group_required("entraineur", "joueur")
def list_attendances(request, event_id):
    return render(request, 'events/list_attendances.html',
        {'event': Event.objects.get(pk=event_id)})

@group_required("entraineur", "joueur")
def my_attendances(request):
    return render(request, 'events/my_attendances.html', {'attendances': Attendance.objects.filter(
        event__event_date__gte=date.today(), attendee=request.user)})


@group_required("entraineur", "joueur")
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