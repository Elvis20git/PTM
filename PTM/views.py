import bcrypt
from sweetify import sweetify
from django.forms import modelformset_factory
from django.contrib.auth import authenticate, login
from django.contrib.auth.context_processors import auth
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
import json
from django.contrib.auth.views import PasswordChangeView
from PTM.models import User, Allprojects, Task
from django.shortcuts import render
from .models import Allprojects
from .models import Meeting
from .forms import MeetingForm, MeetingNoteForm, TaskDeadlineUpdateForm
from django.utils import timezone
from .models import Task, TaskDeadlineUpdate
from .models import MeetingNote
from django.forms import formset_factory
from allauth.account.views import SignupView
from .forms import CustomUserCreationForm, UserChangeForm
from django.urls import reverse_lazy
from django.views.generic import RedirectView
from PTM.models import CustomUser
from .utils import send_project_email
from .utils import send_task_email
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from datetime import datetime
from .decorators import role_required
# from .forms import CustomSignupForm


# from .models import Project

@login_required
def homepage(request):

    return render(request, 'PTM/index.html')

def user_login(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.account_activation:
                login(request, user)
                if user.role == 'user':
                    print(f'Reached as user')
                    # return render(request, 'PTM/userPage.html')
                    return redirect('task_count')
                elif user.role in ['manager', 'admin']:
                    return render(request, 'PTM/dashboard.html')
                else:
                    messages.error(request, 'Role not recognized. Contact support.')
                    return redirect('/')
            else:
                messages.error(request, 'Your account needs to be activated to proceed.')
                return redirect('/')
        else:
            messages.error(request, 'Invalid username or password')
            return redirect('/')

    return render(request, 'PTM/user_login.html')
@login_required
# def dashboard(request):
#
#     return render(request, 'PTM/dashboard.html',{'user': request.user})

def logout(request):

    return render(request, 'PTM/logout.html')

@role_required('admin', 'manager')
@login_required

def projects(request):
        projects = Allprojects.objects.all()
        all_users = CustomUser.objects.all()
        return render(request, 'PTM/projects.html', context = {'projects': projects, 'all_users': all_users})


def get_custom_users(request):
    # Query the CustomUser table to get the usernames
    users = CustomUser.objects.values_list('username', flat=True)
    return JsonResponse({'users': list(users)})
def add_project(request):
    if request.method == "POST":
        project_name = request.POST.get('project_name')
        project_manager = request.POST.get('project_manager')
        ProjectM_tags = request.POST.get('ProjectM_tags')

        try:
            # Convert project_members from JSON string to Python list
            ProjectM_tags = json.loads(ProjectM_tags)

            # Check if the project manager exists in the CustomUser table
            if not CustomUser.objects.filter(username=project_manager).exists():
                return JsonResponse({'error': 'Project manager does not exist'}, status=400)

            # Check if each project member exists in the CustomUser table
            for member_username in ProjectM_tags:
                if not CustomUser.objects.filter(username=member_username['value']).exists():
                    messages.error(request, f'Tagged member {member_username["value"]} does not exist')
                    return JsonResponse({'error': f'Tagged member {member_username["value"]} does not exist'}, status=400)

            allprojects = Allprojects.objects.create(
                project_name=project_name,
                project_manager=project_manager,
                ProjectM_tags=ProjectM_tags  # Assuming your model can handle a list directly
            )
            messages.success(request, 'The project has been added.')

            # Extracting emails from tagged members
            member_emails = [member_username['value'] for member_username in ProjectM_tags]
            send_project_email(member_emails, project_name)

            # return JsonResponse({'success': 'The project has been added successfully.'})
            return redirect('projects')
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)


def edit_project(request, id):
    try:
        project = get_object_or_404(Allprojects, id=id)
    except Allprojects.DoesNotExist:
        return JsonResponse({'error': 'Project not found'}, status=404)

    if request.method == "POST":
        project_name = request.POST.get('project_name')
        project_manager = request.POST.get('project_manager')
        ProjectM_tags = request.POST.get('ProjectM_tags')

        if project_name:
            project.project_name = project_name
        if project_manager:
            project.project_manager = project_manager
        if ProjectM_tags:
            try:
                ProjectM_tags = json.loads(ProjectM_tags)
            except json.JSONDecodeError:
                return JsonResponse({'error': 'Invalid JSON data'}, status=400)
            project.ProjectM_tags = ProjectM_tags

        project.save()
        sweetify.toast(request, 'The project has been updated.', icon='success', duration=3000)
        return redirect('projects')
    else:
        print(f'Project Tags: {project.ProjectM_tags}')
        return render(request, 'PTM/UpdateP.html', {'project': project})

def delete_project(request, project_id):
    # if request.method == "POST":
    try:
        project = Allprojects.objects.get(pk=project_id)
        project.delete()
        print(f'Project to Delete: {project}')
        # return
        return redirect('projects')
    except Allprojects.DoesNotExist:
        return JsonResponse({'error': 'Project not found'}, status=404)


def project_detail(request, project_id):
    project = get_object_or_404(Allprojects, pk=project_id)
    tasks = Task.objects.filter(project=project)
    return render(request, 'project_detail.html', {'project': project, 'tasks': tasks})


def create_task(project_id, task_description, assign_to, deadline, assigned_by, status=1):
    project = Allprojects.objects.get(pk=project_id)
    task = Task.objects.create(
        project=project,
        task_description=task_description,
        assign_to=assign_to,
        deadline=deadline,
        assigned_by=assigned_by,
        status=status
    )
    task.save()
    return task

def search_users(request):
    if 'q' in request.GET:
        query = request.GET.get('q')
        users = CustomUser.objects.filter(username__icontains=query).values('username')
        return JsonResponse(list(users), safe=False)
    return JsonResponse([], safe=False)

# @login_required
@login_required
@role_required('admin', 'manager')
def tasks(request):
    if request.method == "POST":
        print(request.POST)  # Debugging: Print the POST data to see what is being submitted

        project_id = request.POST.get('project')
        task_description = request.POST.get('task_description')
        assigned_to_username = request.POST.get('assigned_to')
        deadline = request.POST.get('deadline')
        assigned_by_username = request.POST.get('assigned_by')
        status = request.POST.get('status')

        # Check if all required fields are provided
        if not all([project_id, task_description, assigned_to_username, deadline, assigned_by_username, status]):
            messages.error(request, 'Please provide all required fields.')
            return redirect('tasks')

        try:
            status = int(status)
        except ValueError:
            messages.error(request, 'Invalid status value.')
            return redirect('tasks')

        try:
            project = Allprojects.objects.get(pk=project_id)
        except Allprojects.DoesNotExist:
            messages.error(request, 'Project does not exist.')
            return redirect('tasks')

        # Ensure assigning user exists
        try:
            assigned_by = CustomUser.objects.get(username=assigned_by_username)
        except CustomUser.DoesNotExist:
            messages.error(request, 'Assigning user does not exist.')
            return redirect('tasks')

        # Ensure assigned user exists
        try:
            assigned_to = CustomUser.objects.get(username=assigned_to_username)
        except CustomUser.DoesNotExist:
            messages.error(request, 'Assigned user does not exist.')
            return redirect('tasks')

        completion_date = timezone.now().date() if status == 2 else None

        task = Task.objects.create(
            project=project,
            task_description=task_description,
            assigned_to=assigned_to,
            deadline=deadline,
            assigned_by=assigned_by,
            status=status,
            completion_date=completion_date
        )

        task.save()

        messages.success(request, 'The Task has been added.')
        send_task_email(
            usernames=[assigned_to.username],
            project_name=project.project_name,
            task_description=task_description,
            assigned_by=assigned_by_username,
            deadline=deadline
        )

        return redirect('allTasks')

    else:
        all_projects = Allprojects.objects.all()
        all_users = CustomUser.objects.all()
        all_tasks = Task.objects.all()
        task_details = TaskDeadlineUpdate.objects.all()


        context = {
            'all_projects': all_projects,
            'all_users': all_users,
            'all_tasks': all_tasks,
            'task_details': task_details,
            # 'completed_tasks_count': completed_tasks_count,
            # 'InProgress_tasks_count': InProgress_tasks_count
        }
        return render(request, 'PTM/tasks.html', context)


def task_count(request):
    user = request.user
    task_count = Task.objects.filter(assigned_to=user).count()
    completed_tasks_count = Task.objects.filter(assigned_to=user, status=2).count()
    in_progress_tasks_count = Task.objects.filter(assigned_to=user, status=3).count()
    overdue_tasks_count = Task.objects.filter(assigned_to=user, status=4).count()
    pending_tasks_count = Task.objects.filter(assigned_to=user, status__in=[1, 4]).count()  # Assuming 1 and 4 are pending statuses

    all_projects = Allprojects.objects.all()
    all_users = CustomUser.objects.all()
    user_tasks = Task.objects.filter(assigned_to=user)
    completed_tasks = user_tasks.filter(status=2)
    in_progress_tasks = user_tasks.filter(status=3)
    overdue_tasks = user_tasks.filter(status=4)
    pending_tasks = user_tasks.filter(status__in=[1, 4])

    context = {
        'task_count': task_count,
        'completed_tasks_count': completed_tasks_count,
        'in_progress_tasks_count': in_progress_tasks_count,
        'pending_tasks_count': pending_tasks_count,
        'user_tasks': user_tasks,
        'completed_tasks': completed_tasks,
        'in_progress_tasks': in_progress_tasks,
        'pending_tasks': pending_tasks,
        'all_projects': all_projects,
        'all_users': all_users,
        'overdue_tasks': overdue_tasks,
        # 'task_details': task_details,
    }
    return render(request, 'PTM/userPage.html', context)


def completed_tasks(request):
    # Get the current logged-in user
    current_user = request.user

    # Filter tasks with status=2 (Completed) assigned to the current user
    completed_tasks = Task.objects.filter(assigned_to=current_user, status=2)

    context = {
        'completed_tasks': completed_tasks,
    }
    return render(request, 'PTM/userPage.html', context)

def in_progress_tasks(request):
    # Get the current logged-in user
    current_user = request.user

    # Filter tasks with status=3 (In Progress) assigned to the current user
    In_Progress_tasks= Task.objects.filter(assigned_to=current_user, status=3)


    context = {
        'in_progress_tasks': in_progress_tasks,
    }
    return render(request, 'PTM/userPage.html', context)


def overdue_tasks(request):
    # Get the current logged-in user
    current_user = request.user
    print("View called")

    # Filter tasks with status indicating overdue (assuming status=4 for Overdue)
    overdue_tasks = Task.objects.filter(assigned_to=current_user, status=4)

    for task in overdue_tasks:
        print(f"Task: {task.task_description}, Project: {task.project.project_name}, Deadline: {task.deadline}")

    context = {
        'overdue_tasks': overdue_tasks,
    }
    return render(request, 'PTM/userPage.html', context)
# @login_required

@login_required
def edit_task(request, task_id):
    task = get_object_or_404(Task, pk=task_id)
    user_role = request.user.role  # Assuming you have a role attribute in your CustomUser model

    if request.method == "POST":
        # Debugging: Print the POST data
        print(request.POST)

        project_id = request.POST.get('project')
        task_description = request.POST.get('task_description')
        assigned_to_username = request.POST.get('assigned_to')
        assigned_by_username = request.POST.get('assigned_by')
        deadline = request.POST.get('deadline')
        status = request.POST.get('status')

        # Check if all required fields are provided
        if not status:
            messages.error(request, 'Please provide all required fields.')
            return redirect('edit_task', task_id=task_id)

        try:
            if user_role in ['manager', 'admin']:
                task.project_id = project_id
                task.task_description = task_description

                # Ensure assigned user exists
                try:
                    assigned_to = CustomUser.objects.get(username=assigned_to_username)
                except CustomUser.DoesNotExist:
                    messages.error(request, 'Assigned user does not exist.')
                    return redirect('edit_task', task_id=task_id)

                # Ensure assigning user exists
                try:
                    assigned_by = CustomUser.objects.get(username=assigned_by_username)
                except CustomUser.DoesNotExist:
                    messages.error(request, 'Assigning user does not exist.')
                    return redirect('edit_task', task_id=task_id)

                task.assigned_to = assigned_to
                task.assigned_by = assigned_by

                # Parse the deadline date
                try:
                    task.deadline = datetime.strptime(deadline, '%B %d, %Y').date()
                except ValueError:
                    messages.error(request, 'Invalid deadline date format. It must be in "Month DD, YYYY" format.')
                    return redirect('edit_task', task_id=task_id)

            task.status = status

            if int(task.status) == 2:  # Completed
                task.completion_date = timezone.now().date()

            task.save()

            messages.success(request, 'The Task has been updated.')
            return redirect('allTasks')

        except Exception as e:
            messages.error(request, f'An error occurred: {e}')
            return redirect('edit_task', task_id=task_id)

    else:
        all_projects = Allprojects.objects.all()
        read_only = user_role == 'user'
        context = {
            'task': task,
            'all_projects': all_projects,
            'read_only': read_only,
        }
        return render(request, 'PTM/updateTask.html', context)




# def edit_task(request, task_id):
#     if request.method == "POST":
#         task = get_object_or_404(Task, pk=task_id)
#
#         # Debugging: Print the POST data
#         print(request.POST)
#
#         project_id = request.POST.get('project')
#         task_description = request.POST.get('task_description')
#         assigned_to_username = request.POST.get('assigned_to')
#         assigned_by_username = request.POST.get('assigned_by')
#         deadline = request.POST.get('deadline')
#         status = request.POST.get('status')
#
#         # Check if all required fields are provided
#         if not all([project_id, task_description, assigned_to_username, assigned_by_username, deadline, status]):
#             messages.error(request, 'Please provide all required fields.')
#             return redirect('edit_task', task_id=task_id)
#
#         try:
#             task.project_id = project_id
#             task.task_description = task_description
#
#             # Ensure assigned user exists
#             try:
#                 assigned_to = CustomUser.objects.get(username=assigned_to_username)
#             except CustomUser.DoesNotExist:
#                 messages.error(request, 'Assigned user does not exist.')
#                 return redirect('edit_task', task_id=task_id)
#
#             # Ensure assigning user exists
#             try:
#                 assigned_by = CustomUser.objects.get(username=assigned_by_username)
#             except CustomUser.DoesNotExist:
#                 messages.error(request, 'Assigning user does not exist.')
#                 return redirect('edit_task', task_id=task_id)
#
#             task.assigned_to = assigned_to
#             task.assigned_by = assigned_by
#
#             # Parse the deadline date
#             try:
#                 task.deadline = datetime.strptime(deadline, '%B %d, %Y').date()
#             except ValueError:
#                 messages.error(request, 'Invalid deadline date format. It must be in "Month DD, YYYY" format.')
#                 return redirect('edit_task', task_id=task_id)
#
#             task.status = status
#
#             if int(task.status) == 2:  # Completed
#                 task.completion_date = timezone.now().date()
#
#             task.save()
#
#             messages.success(request, 'The Task has been updated.')
#             return redirect('allTasks')
#
#         except Exception as e:
#             messages.error(request, f'An error occurred: {e}')
#             return redirect('edit_task', task_id=task_id)
#
#     else:
#         task = get_object_or_404(Task, pk=task_id)
#         all_projects = Allprojects.objects.all()
#         context = {
#             'task': task,
#             'all_projects': all_projects,
#         }
#         return render(request, 'PTM/updateTask.html', context)

@role_required('admin', 'manager')
@login_required
def allTasks(request):
    all_projects = Allprojects.objects.all()
    all_tasks = Task.objects.all()
    context = {
        'all_projects': all_projects,
        'all_tasks': all_tasks,


    }

    return render(request, 'PTM/alltasks.html', context)

@role_required('admin', 'manager')
@login_required
def update_task_deadline(request, task_id):
    task = get_object_or_404(Task, pk=task_id)
    if request.method == "POST":
        form = TaskDeadlineUpdateForm(request.POST)
        if form.is_valid():
            new_deadline = form.cleaned_data['new_deadline']
            impact_on_result = form.cleaned_data['impact_on_result']
            comment = form.cleaned_data['comment']

            # Update the task's deadline
            task.revised_due_date = new_deadline
            task.old_deadline = task.deadline
            task.save()

            # Create an instance of TaskDeadlineUpdate and save it
            task_deadline_update = TaskDeadlineUpdate(
                task=task,
                old_deadline=task.deadline,
                new_deadline=new_deadline,
                impact_on_result=impact_on_result,
                comment=comment
            )
            task_deadline_update.save()

            messages.success(request, 'The task deadline has been updated.')
            return redirect('allTasks')
        else:
            print("Form is invalid:", form.errors)
    else:
        form = TaskDeadlineUpdateForm(initial={'new_deadline': task.revised_due_date and task.deadline, 'old_deadline': task.deadline})

    context = {
        'form': form,
        'task': task
    }
    return render(request, 'PTM/UpdateDeadline.html', context)
def task_update_list(request):
    updates = TaskDeadlineUpdate.objects.all()

    context = {
        'updates': updates
    }
    return render(request, 'PTM/updatedDeadlineList.html', context)

def delete_task(request, task_id):
    # if request.method == "POST":
    try:
        task = Task.objects.get(pk=task_id)
        task.delete()
        return redirect('allTasks')
    except Task.DoesNotExist:
        return JsonResponse({'error': 'Task not found'}, status=404)

@role_required('admin', 'manager')
def addUser(request):

    if request.method == "POST":
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        username = request.POST['username']
        email = request.POST['email']
        department = request.POST['department']
        password = request.POST['password']
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())


        myuser = User.objects.create(username=username, email=email, password=password)
        myuser.first_name = first_name
        myuser.last_name = last_name
        myuser.department = department

        myuser.save()
        messages.success(request, 'Your account has been created!')
        return redirect('user_login')
    return render(request, 'PTM/addUser.html', {'user': request.user})
# @login_required

@role_required('admin', 'manager')
def dashboard(request):
    # Retrieve the count of projects from the database
    project_count = Allprojects.objects.count()
    task_count = Task.objects.count()
    user_count = CustomUser.objects.count()
    completed_tasks_count = Task.objects.filter(status=2).count()
    in_progress_tasks_count = Task.objects.filter(status=3).count()
    overDue_tasks_count = Task.objects.filter(status=4).count()
    open_tasks_count = Task.objects.filter(status=1).count()
    # Pass the project count to the template context

    context = {
        'project_count': project_count,
        'task_count': task_count,
        'user_count': user_count,
        'completed_tasks_count': completed_tasks_count,
        'in_progress_tasks_count': in_progress_tasks_count,
        'overDue_tasks_count': overDue_tasks_count,
        'open_tasks_count': open_tasks_count
    }
    return render(request, 'PTM/Dashboard.html', context)


@role_required('admin', 'manager')
def allUser(request):
    return render(request, 'PTM/allUser.html')

@login_required
def create_meeting(request):
    MeetingNoteFormSet = modelformset_factory(MeetingNote, form=MeetingNoteForm, extra=1)

    projects = Allprojects.objects.all()

    if request.method == 'POST':
        meeting_form = MeetingForm(request.POST, projects=projects)
        meeting_note_formset = MeetingNoteFormSet(request.POST, queryset=MeetingNote.objects.none())

        if meeting_form.is_valid() and meeting_note_formset.is_valid():
            meeting = meeting_form.save()

            for form in meeting_note_formset:
                meeting_note = form.save(commit=False)
                meeting_note.meeting = meeting
                meeting_note.save()

                if meeting_note.note_type == 'action':
                    create_task(
                        project_id=meeting.project.id,
                        task_description=meeting_note.note_content,
                        assign_to=meeting_note.assigned_to,
                        deadline=meeting_note.deadline_date,
                        assigned_by=meeting_note.assigned_by
                    )

            return redirect('meeting_list')
        else:
            print(f'Meeting Form Error {meeting_form.errors}')
            print(f'Note Formset Error {meeting_note_formset.errors}')
    else:
        meeting_form = MeetingForm(projects=projects)
        meeting_note_formset = MeetingNoteFormSet(queryset=MeetingNote.objects.none())

    context = {
        'meeting_form': meeting_form,
        'meeting_note_formset': meeting_note_formset,
        'all_projects': projects,
    }
    return render(request, 'PTM/meetingMinutes.html', context)



def meeting_list(request):
    # Get all meeting notes
    meetings = MeetingNote.objects.all()

    # Filter meetings where Note Type is 'action'
    action_meetings = meetings.filter(note_type='action')

    # Pass meetings and a flag to hide 'Decided By' to the template
    return render(request, 'PTM/meetingMinutesList.html', {
        'meetings': meetings,
        'hide_decided_by': True if action_meetings.exists() else False
    })

def meeting_detail(request, meeting_id):
    meeting = get_object_or_404(Meeting, pk=meeting_id)
    return render(request, 'meeting_detail.html', {'meeting': meeting})

def update_meeting(request, meeting_id):
    meeting = get_object_or_404(Meeting, pk=meeting_id)
    if request.method == 'POST':
        form = MeetingForm(request.POST, instance=meeting)
        if form.is_valid():
            form.save()
            return redirect('meeting_detail', meeting_id=meeting_id)
    else:
        form = MeetingForm(instance=meeting)
    return render(request, 'update_meeting.html', {'form': form})

@role_required('admin', 'manager')
def delete_meeting(request, meeting_id):
    meeting = get_object_or_404(Meeting, pk=meeting_id)
    if request.method == 'POST':
        meeting.delete()
        return redirect('meeting_list')
    return render(request, 'delete_meeting.html', {'meeting': meeting})
def profile(request):
    return render(request, 'PTM/profile.html', {'user': request.user})

def edit_profile(request):
    if request.method == 'POST':
        user_form = CustomUserChangeForm(request.POST, instance=request.user)
        if user_form.is_valid():
            user_form.save()
            return redirect('profile')
    else:
        user_form = CustomUserChangeForm(instance=request.user)
    return render(request, 'PTM/edit_profile.html', {'user_form': user_form})

def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            return redirect('user_login')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'PTM/change_password.html', {'form': form})

class CustomPasswordChangeView(PasswordChangeView):
    template_name = 'PTM/change_password.html'  # Ensure this matches your template name
    success_url = reverse_lazy('logout')  # Redirect to login page after logout

    def form_valid(self, form):
        response = super().form_valid(form)
        logout(self.request)
        return response

@role_required('admin', 'manager')
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('user_login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'PTM/register.html', {'form': form})

def manager_list(request):
    all_users = CustomUser.objects.all()
    managers = all_users.filter(role='manager')
    context = {
        'all_users': all_users,
        'managers': managers,
    }
    return render(request, 'PTM/tasks.html', context)

def is_user(user):
    return user.role == 'user'

@login_required
@user_passes_test(is_user)
def user_tasks(request):
    user = request.user
    tasks = Task.objects.filter(assign_to=user)
    return render(request, 'PTM/user_tasks.html', {'tasks': tasks})

@login_required
def notifications(request):
    current_user = request.user
    notifications = Notification.objects.filter(user=current_user).order_by('-created_at')
    context = {
        'notifications': notifications,
    }
    return render(request, 'PTM/notifications.html', context)

@login_required
def get_notifications(request):
    current_user = request.user
    notifications = Notification.objects.filter(user=current_user, is_read=False).order_by('-created_at')
    notifications_list = [
        {
            'message': notification.message,
            'created_at': notification.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        }
    for notification in notifications]
    notifications.update(is_read=True)
    return JsonResponse({'notifications': notifications_list})