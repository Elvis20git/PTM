from django.urls import path, include
from . import views, admin
from .views import update_task_deadline

urlpatterns = [
    path('', views.homepage, name=""),
    path('register', views.register, name="register"),
    path('user_login', views.user_login, name="user_login"),
    path('dashboard', views.dashboard, name="dashboard"),
    path('logout', views.logout, name="logout"),
    path('projects', views.projects, name="projects"),
    path('tasks', views.tasks, name="tasks"),
    path('addUser', views.addUser, name="addUser"),
    path('User', views.addUser, name="User"),
    path('allUser', views.allUser, name="allUser"),
    path('create_meeting', views.create_meeting, name="create_meeting"),
    path('profile', views.profile, name="profile"),
    path('add_project', views.add_project, name="add_project"),
    path('delete_project/<int:project_id>', views.delete_project, name="delete_project"),
    path('edit_project/<int:id>', views.edit_project, name="edit_project"),
    path('delete_task/<int:task_id>', views.delete_task, name="delete_task"),
    path('edit_task/<int:task_id>', views.edit_task, name="edit_task"),
    path('update_task_deadline/<int:task_id>/', update_task_deadline, name='update_task_deadline'),
    path('meeting_list', views.meeting_list, name="meeting_list"),
    path('meeting_detail/<int:meeting_id>', views.meeting_detail, name="meeting_detail"),
    path('task_update_list/', views.task_update_list, name="task_update_list"),
    path('meeting_list/', views.meeting_list, name="meeting_list"),
    # path('account/signup', custom_signup_view, name="signup"),
    # path('accounts/', include('allauth.urls')),


]
