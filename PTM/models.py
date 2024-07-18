from django.contrib.auth.models import User
from django.db import models
from django.db.models import JSONField
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.conf import settings
# Create your models here.

class MyModel(models.Model):
    tags = JSONField()


class CustomUser(AbstractUser):
    # Your custom fields here
    full_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    account_activation = models.BooleanField(default=False)
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('manager', 'Manager'),
        ('user', 'User'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')

    # Specify unique related names for groups and user_permissions fields
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        related_name='customuser_set',  # Specify a unique related name
        related_query_name='user',
    )

    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        related_name='customuser_set',  # Specify a unique related name
        related_query_name='user',
    )

    def __str__(self):
        return self.username

class Allprojects(models.Model):
    project_name = models.CharField(max_length=100)
    project_manager = models.CharField(max_length=100)
    ProjectM_tags = models.JSONField(default=list)  # Field to store member names

    def __str__(self):
        return self.project_name


class Task(models.Model):
    project = models.ForeignKey(Allprojects, on_delete=models.CASCADE)
    task_description = models.CharField(max_length=255)
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='assigned_tasks')
    # assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    deadline = models.DateField()
    revised_due_date = models.DateField(null=True, blank=True)
    completion_date = models.DateField(blank=True, null=True)
    assigned_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='tasks_assigned')
    status = models.IntegerField(choices=[(1, 'Not Started'), (2, 'Completed'), (3, 'In Progress'), (4, 'Overdue')],
                                 default=1)

    def __str__(self):
        return self.task_description

# class Tasks(models.Model):
#     title = models.CharField(max_length=200)
#     description = models.TextField()
#     # assigned_to = models.ForeignKey(User, on_delete=models.CASCADE)
#     assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
#     def __str__(self):
#         return self.title


class TaskDeadlineUpdate(models.Model):
    IMPACT_CHOICES = [
        ('overdue_no_impact', 'Overdue - No impact on final result'),
        ('overdue_impact', 'Overdue - Impact on final result'),
    ]

    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    old_deadline = models.DateField()
    new_deadline = models.DateField()
    impact_on_result = models.CharField(max_length=30, choices=IMPACT_CHOICES, blank=True, null=True)
    comment = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Update for {self.task.task_description} - New Deadline: {self.new_deadline}"

class UpdatedTask(models.Model):
    pass


class Meeting(models.Model):
    project = models.ForeignKey(Allprojects, on_delete=models.CASCADE, related_name='meetings')
    meeting_date = models.DateField(blank=True, null=True)
    meeting_time = models.TimeField(blank=True, null=True)
    # notes = models.TextField()

    def __str__(self):
        return f"Meeting on {self.meeting_date} for {self.project.project_name}"


class NoteType(models.TextChoices):
    NOTE = 'note', 'Note'
    DECISION = 'decision', 'Decision'
    ACTION = 'action', 'Action'


class MeetingNote(models.Model):
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE, related_name='meeting_notes')
    note_type = models.CharField(max_length=10, choices=NoteType.choices,blank=True, null=True)
    note_content = models.TextField(blank=True, null=True)
    decided_by = models.CharField(max_length=200, blank=True, null=True)
    assigned_to = models.CharField(max_length=200, blank=True, null=True)
    assigned_by = models.CharField(max_length=200, blank=True, null=True)
    deadline_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"{self.get_note_type_display()} for {self.meeting}"


class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Notification for {self.user.username}: {self.message}'
