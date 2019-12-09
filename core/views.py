from django.http import HttpResponse
from django.shortcuts import render, render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from datetime import date
from core.forms import SignUpForm, CreateEventForm
from core.decorators import group_required
from core.models import Event, Attendance

def index(request):
    return render(request, 'index.html')

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('index')
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
            return redirect('index')
    else:
        form = AuthenticationForm()
    return render(request, 'signin.html', {'form': form})

@group_required("entraineur")
def create_event(request):
    if request.method == 'POST':
        form = CreateEventForm(request.POST)
        if form.is_valid():
            form.cleaned_data['added_by'] = request.user
            new_event = form.save()
            # Create attendance for all players
            for u in User.objects.filter(groups__name='joueur'):
                Attendance.objects.create(event=new_event, attendee=u, is_attending=None)
            return redirect('list_events')
    else:
        form = CreateEventForm(initial={'added_by': request.user})
    return render(request, 'events/create.html', {'form': form})

@group_required("entraineur")
def list_events(request):
    return render(request, 'events/list.html', {'events': Event.objects.filter(event_date__gte=date.today())})

@group_required("entraineur")
def list_attendances(request, event_id):
    return render(request, 'events/list_attendances.html',
        {'event': Event.objects.get(pk=event_id)})

@group_required("joueur")
def my_attendances(request):
    return render(request, 'events/my_attendances.html', {'attendances': Attendance.objects.filter(
        event__event_date__gte=date.today(), attendee=request.user)})