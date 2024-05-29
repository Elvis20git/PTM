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
import json
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
# from .forms import CustomSignupForm


# from .models import Project

def homepage(request):

    return render(request, 'PTM/index.html')

def register(request):
    if request.method == "POST":
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        phone_number = request.POST['phone']
        email = request.POST['email']
        department = request.POST['department']
        password = request.POST['password']

        myuser = User.objects.create_user(email=email, password=password)
        myuser.first_name = first_name
        myuser.last_name = last_name
        myuser.phone_number = phone_number
        myuser.department = department

        myuser.save()
        messages.success(request, 'Your account has been created!')
        return redirect('login')


    return render(request, 'PTM/register.html')

def user_login(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=username, password=password)
        print(f'User logged in: {user}')
        if user is not None:
            login(request, user)
            return render(request, "PTM/dashboard.html")

        else:
            messages.error(request, 'Invalid username or password')
            return redirect('user_login')



    return render(request, 'PTM/user_login.html')

def dashboard(request):

    return render(request, 'PTM/dashboard.html')

def logout(request):

    return render(request, 'PTM/logout.html')


def projects(request):
        projects = Allprojects.objects.all()
        return render(request, 'PTM/projects.html', {'projects': projects})

def add_project(request):
    if request.method == "POST":
        project_name = request.POST['project_name']
        project_manager = request.POST['project_manager']
        ProjectM_tags = request.POST['ProjectM_tags']
        try:
            # Attempt to load JSON from string to ensure it's properly formatted and stored
            ProjectM_tags = json.loads(ProjectM_tags)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)

        allprojects = Allprojects.objects.create(project_name=project_name, project_manager=project_manager, ProjectM_tags=ProjectM_tags)
        allprojects.save()
        messages.success(request, 'The project has been added.')
        # sweetify.toast(request, 'The project has been added.', icon='success', duration=3000)
        return redirect('projects')


def edit_project(request, id):
    # project = Allprojects.objects.get(id=id)

    if request.method == "POST":
        # Fetch the project instance to update
        try:
            project = Allprojects.objects.get(id=id)
        except Allprojects.DoesNotExist:
            return JsonResponse({'error': 'Project not found'}, status=404)

        # Update project fields based on the form data
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

        # Save the updated project instance
        project.save()
        sweetify.toast(request, 'The project has been updated.', icon='success', duration=3000)
        return redirect('projects')
    else:
        # If it's a GET request, fetch the project instance and render the edit form
        try:
            project = Allprojects.objects.get(id=id)
        except Allprojects.DoesNotExist:
            return JsonResponse({'error': 'Project not found'}, status=404)

        print(f'Project Tags: {[tag for tag in project.ProjectM_tags]}')
        # Render the edit form with the project instance
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

def tasks(request):
    if request.method == "POST":
        project_id = request.POST['project']
        task_description = request.POST['task_description']
        assign_to = request.POST['assign_to']
        deadline = request.POST['deadline']
        assigned_by = request.POST['assigned_by']
        status = int(request.POST['status'])

        project = Allprojects.objects.get(pk=project_id)
        completion_date = timezone.now().date() if status == 2 else None

        task = Task.objects.create(
            project=project,
            task_description=task_description,
            assign_to=assign_to,
            deadline=deadline,
            assigned_by=assigned_by,
            status=status,
            completion_date=completion_date
        )
        task.save()
        messages.success(request, 'The Task has been added.')
        return redirect('tasks')

    else:
        all_projects = Allprojects.objects.all()
        all_tasks = Task.objects.all()
        context = {
            'all_projects': all_projects,
            'all_tasks': all_tasks
        }
        return render(request, 'PTM/tasks.html', context)
def edit_task(request, task_id):
    if request.method == "POST":
        task = get_object_or_404(Task, pk=task_id)
        task.project_id = request.POST['project']
        task.task_description = request.POST['task_description']
        task.assign_to = request.POST['assign_to']
        task.deadline = request.POST['deadline']
        task.assigned_by = request.POST['assigned_by']
        task.status = request.POST['status']

        if int(task.status) == 2:  # Completed
            task.completion_date = timezone.now().date()
        # Trackchanges.objects.create(task = task, new_deadline=request.POST['deadline'],comment = )
        task.save()


        return redirect('tasks')

    else:
        task = get_object_or_404(Task, pk=task_id)
        all_projects = Allprojects.objects.all()
        context = {
            'task': task,
            'all_projects': all_projects,
        }
        return render(request, 'PTM/updateTask.html', context)


def update_task_deadline(request, task_id):
    task = get_object_or_404(Task, pk=task_id)

    if request.method == "POST":
        form = TaskDeadlineUpdateForm(request.POST)
        if form.is_valid():
            task_update = form.save(commit=False)
            task_update.task = task
            task_update.old_deadline = task.deadline
            task_update.save()
            print("Task update saved successfully.")
            task.deadline = task_update.new_deadline
            task.save()
            print("Task deadline updated successfully.")
            messages.success(request, 'The task deadline has been updated.')
            return redirect('tasks')
        else:
            print("Form is invalid:", form.errors)
    else:
        form = TaskDeadlineUpdateForm(initial={'task': task, 'old_deadline': task.deadline})

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
        return redirect('tasks')
    except Task.DoesNotExist:
        return JsonResponse({'error': 'Task not found'}, status=404)

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
    return render(request, 'PTM/addUser.html')

def dashboard(request):
    # Retrieve the count of projects from the database
    project_count = Allprojects.objects.count()
    task_count = Task.objects.count()
    completed_tasks_count = Task.objects.filter(status=2).count()
    in_progress_tasks_count = Task.objects.filter(status=3).count()
    overDue_tasks_count = Task.objects.filter(status=4).count()
    open_tasks_count = Task.objects.filter(status=1).count()
    # Pass the project count to the template context
    context = {
        'project_count': project_count,
        'task_count': task_count,
        'completed_tasks_count': completed_tasks_count,
        'in_progress_tasks_count': in_progress_tasks_count,
        'overDue_tasks_count': overDue_tasks_count,
        'open_tasks_count': open_tasks_count
    }
    return render(request, 'PTM/Dashboard.html', context)


def allUser(request):
    return render(request, 'PTM/allUser.html')


def create_meeting(request):
    MeetingNoteFormSet = modelformset_factory(MeetingNote, form=MeetingNoteForm, extra=1)

    if request.method == 'POST':
        meeting_form = MeetingForm(request.POST)
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

            return redirect('dashboard')
        else:
            print(f'Meeting Form Error {meeting_form.errors}')
            print(f'Note Formset Error {meeting_note_formset.errors}')
    else:
        meeting_form = MeetingForm()
        meeting_note_formset = MeetingNoteFormSet(queryset=MeetingNote.objects.none())

    context = {
        'meeting_form': meeting_form,
        'meeting_note_formset': meeting_note_formset,
        'all_projects': Allprojects.objects.all(),
    }
    return render(request, 'PTM/meetingMinutes.html', context)

def meeting_list(request):
    meetings = MeetingNote.objects.all()
    return render(request, 'PTM/meetingMinutesList.html', {'meetings': meetings})

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

def delete_meeting(request, meeting_id):
    meeting = get_object_or_404(Meeting, pk=meeting_id)
    if request.method == 'POST':
        meeting.delete()
        return redirect('meeting_list')
    return render(request, 'delete_meeting.html', {'meeting': meeting})
def profile(request):
    return render(request, 'PTM/profile.html')


# class CustomSignupView(SignupView):
#     form_class = CustomSignupForm
#
#     def form_valid(self, form):
#         response = super().form_valid(form)
#         # Additional logic after form is successfully validated
#         # For example, send a notification to the admin about the new user
#         return response
#
# custom_signup_view = CustomSignupView.as_view()