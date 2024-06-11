from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .views import update_task_deadline, register, CustomPasswordChangeView, get_custom_users

urlpatterns = [
    # User Authentication
    path('register/', register, name='register'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', views.logout, name='logout'),

    # Dashboard and Profile
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/change_password/', views.change_password, name='change_password'),
    path('password_change/', CustomPasswordChangeView.as_view(), name='password_change'),

    # Projects and Tasks
    path('projects/', views.projects, name='projects'),
    path('tasks', views.tasks, name='tasks'),
    path('allTasks', views.allTasks, name='allTasks'),
    path('add_project', views.add_project, name='add_project'),
    path('delete_project/<int:project_id>/', views.delete_project, name='delete_project'),
    path('edit_project/<int:id>/', views.edit_project, name='edit_project'),
    path('project_detail/<int:project_id>/', views.project_detail, name='project_detail'),
    path('delete_task/<int:task_id>/', views.delete_task, name='delete_task'),
    path('edit_task/<int:task_id>/', views.edit_task, name='edit_task'),
    path('update_task_deadline/<int:task_id>/', update_task_deadline, name='update_task_deadline'),

    # Users Management
    path('addUser/', views.addUser, name='addUser'),
    path('User/', views.addUser, name='User'),
    path('allUser/', views.allUser, name='allUser'),
    path('get_custom_users/', get_custom_users, name='get_custom_users'),

    # Meetings
    path('create_meeting/', views.create_meeting, name='create_meeting'),
    path('meeting_list/', views.meeting_list, name='meeting_list'),
    path('meeting_detail/<int:meeting_id>/', views.meeting_detail, name='meeting_detail'),

    # Miscellaneous
    path('task_update_list/', views.task_update_list, name='task_update_list'),

    # Home
    path('', views.user_login, name='user_login'),
]
