from django.urls import path
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('signup', views.signup, name='signup'),
    path('signout', views.signout, name='signout'),
    path('signin', views.signin, name='signin'),
    path('account_activation_sent', views.account_activation_sent, name='account_activation_sent'),
    path('activate/<uidb64>/<token>', views.activate, name='activate'),
    path('events/create', views.create_event, name='create_event'),
    path('events/list', views.list_events, name='list_events'),
    path('events/<int:event_id>/attendances', views.list_attendances, name='list_attendances'),
    path('events/my-attendances', views.my_attendances, name='my_attendances'),
    path('events/my-attendances/<int:attendance_id>', views.my_attendance, name='my_attendance'),
    path('events/player-selection/<int:attendance_id>', views.player_selection, name='player_selection'),
    path('events/<int:event_id>/assign-tasks', views.assign_tasks, name='assign_tasks'),
    path('users/list', views.list_users, name='list_users'),
    path('change-password/', views.change_password, name='change_password'),
]