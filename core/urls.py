from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('signup', views.signup, name='signup'),
    path('signout', views.signout, name='signout'),
    path('signin', views.signin, name='signin'),
    path('events/create', views.create_event, name='create_event'),
    path('events/list', views.list_events, name='list_events'),
    path('events/<int:event_id>/attendances', views.list_attendances, name='list_attendances'),
    path('events/my-attendances', views.my_attendances, name='my_attendances'),
    path('events/my-attendances/<int:attendance_id>', views.my_attendance, name='my_attendance'),
]