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
# from .forms import CustomSignupForm


# from .models import Project

@login_required
def homepage(request):

    return render(request, 'PTM/index.html')

# def register(request):
#     if request.method == "POST":
#         first_name = request.POST['first_name']
#         last_name = request.POST['last_name']
#         phone_number = request.POST['phone']
#         email = request.POST['email']
#         department = request.POST['department']
#         password = request.POST['password']
#
#         myuser = User.objects.create_user(email=email, password=password)
#         myuser.first_name = first_name
#         myuser.last_name = last_name
#         myuser.phone_number = phone_number
#         myuser.department = department
#
#         myuser.save()
#         messages.success(request, 'Your account has been created!')
#         return redirect('user_login')
#
#
#     return render(request, 'PTM/register.html')

def user_login(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=username, password=password)
        if user is not None:
            if user.account_activation:
                login(request, user)
                return render(request, "PTM/dashboard.html")
            else:
                messages.error(request, 'Your account needs to be activated to proceed.')
                return redirect('/')
        else:
            messages.error(request, 'Invalid username or password')
            return redirect('/')

    return render(request, 'PTM/user_login.html')

@login_required
def dashboard(request):

    return render(request, 'PTM/dashboard.html',{'user': request.user})

def logout(request):

    return render(request, 'PTM/logout.html')

@login_required

def projects(request):
        projects = Allprojects.objects.all()
        return render(request, 'PTM/projects.html', {'projects': projects})


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
            # Attempt to load JSON from string to ensure it's properly formatted and stored
            ProjectM_tags = json.loads(ProjectM_tags)
            # Check if the project manager exists in the CustomUser table
            if not CustomUser.objects.filter(username=project_manager).exists():
                return JsonResponse({'error': 'Project manager does not exist'}, status=400)

            # Check if each tagged member exists in the CustomUser table
            for member in ProjectM_tags:
                if not CustomUser.objects.filter(username=member['value']).exists():
                    messages.error(request, f'Tagged member {member["value"]} does not exist')
                    # return JsonResponse({'error': f'Tagged member {member["value"]} does not exist'}, status=400)

            allprojects = Allprojects.objects.create(
                project_name=project_name,
                project_manager=project_manager,
                ProjectM_tags=ProjectM_tags
            )
            # allprojects.save()
            messages.success(request, 'The project has been added.')

            # Extracting emails from tagged members
            member_emails = [member['value'] for member in ProjectM_tags]
            # member_emails = [CustomUser.objects.get(username=member['value']).email for member in ProjectM_tags]
            send_project_email(member_emails, project_name)

            return redirect('projects')
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)

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

@login_required
def tasks(request):
    if request.method == "POST":
        project_id = request.POST['project']
        task_description = request.POST['task_description']
        assign_to_username = request.POST['assign_to']
        deadline = request.POST['deadline']
        assigned_by = request.POST['assigned_by']
        status = int(request.POST['status'])

        # Ensure assigned user exists
        try:
            assign_to = CustomUser.objects.get(username=assign_to_username)
        except CustomUser.DoesNotExist:
            messages.error(request, 'Assigned user does not exist')
            return redirect('tasks')

        project = Allprojects.objects.get(pk=project_id)
        completion_date = timezone.now().date() if status == 2 else None

        task = Task.objects.create(
            project=project,
            task_description=task_description,
            assign_to=assign_to.username,
            deadline=deadline,
            assigned_by=assigned_by,
            status=status,
            completion_date=completion_date
        )
        task.save()
        messages.success(request, 'The Task has been added.')
        send_task_email([assign_to.username], project.project_name, task_description)
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
            'task_details': task_details
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


        return redirect('allTasks')

    else:
        task = get_object_or_404(Task, pk=task_id)
        all_projects = Allprojects.objects.all()
        context = {
            'task': task,
            'all_projects': all_projects,
        }
        return render(request, 'PTM/updateTask.html', context)

def allTasks(request):
    all_projects = Allprojects.objects.all()
    all_tasks = Task.objects.all()

    paginator = Paginator(all_tasks, 10)
    page_number = request.GET.get('page')
    all_tasks = paginator.get_page(page_number)

    context = {
        'all_projects': all_projects,
        'all_tasks': all_tasks

    }

    return render(request, 'PTM/alltasks.html', context)
# def update_task_deadline(request, task_id):
#     task = get_object_or_404(Task, pk=task_id)
#
#     if request.method == "POST":
#         form = TaskDeadlineUpdateForm(request.POST)
#         if form.is_valid():
#             task_update = form.save(commit=False)
#             task_update.task = task
#             task_update.old_deadline = task.deadline
#             task_update.save()
#             print("Task update saved successfully.")
#             task.deadline = task_update.new_deadline
#             task.save()
#             print("Task deadline updated successfully.")
#             messages.success(request, 'The task deadline has been updated.')
#             return redirect('tasks')
#         else:
#             print("Form is invalid:", form.errors)
#     else:
#         form = TaskDeadlineUpdateForm(initial={'task': task, 'old_deadline': task.deadline})
#
#     context = {
#         'form': form,
#         'task': task
#     }
#     return render(request, 'PTM/UpdateDeadline.html', context)

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
@login_required
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


def allUser(request):
    return render(request, 'PTM/allUser.html')

@login_required
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

# def meeting_list(request):
#     meetings = MeetingNote.objects.all()
#     return render(request, 'PTM/meetingMinutesList.html', {'meetings': meetings})

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
        logout(self.request)  # Log out the user
        return response
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

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('user_login')  # Redirect to a login page or success page
    else:
        form = CustomUserCreationForm()
    return render(request, 'PTM/register.html', {'form': form})