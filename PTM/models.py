from django.contrib.auth.models import User
from django.db import models
from django.db.models import JSONField
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
# Create your models here.

class MyModel(models.Model):
    tags = JSONField()
# class Profile(models.Model):
#     user = models.OneToOneField(User, null=True, on_delete=models.CASCADE)
#     department = models.CharField(max_length=100)
#     def __str__(self):
#         return str(self.user)
# class Alluser(models.Model):
#     first_name = models.CharField(max_length=100)
#     last_name = models.CharField(max_length=100)
#     username = models.CharField(max_length=15)
#     email = models.EmailField()
#     department = models.CharField(max_length=100, choices=[
#         ('quality_assurance', 'Quality Assurance'),
#         ('finance', 'Finance'),
#     ])
#     password = models.CharField(max_length=100)

class User(AbstractUser):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(unique=True)
    department = models.CharField(max_length=100)
    password = models.CharField(max_length=100)

class Allprojects(models.Model):
    project_name = models.CharField(max_length=100)
    project_manager = models.CharField(max_length=100)
    ProjectM_tags = models.JSONField(default=list)  # Field to store member names

    def __str__(self):
        return self.project_name

class Task(models.Model):
    project = models.ForeignKey(Allprojects, on_delete=models.CASCADE)
    task_description = models.CharField(max_length=255)
    assign_to = models.CharField(max_length=100)
    deadline = models.DateField()
    completion_date = models.DateField(blank=True, null=True)
    assigned_by = models.CharField(max_length=100)
    status = models.IntegerField(choices=[(1, 'Open'), (2, 'Completed'), (3, 'In Progress'), (4, 'Overdue')], default=1)
    # progress = models.IntegerField(choices=[(0, '0%'), (10, '10%'), (20, '20%'), (30, '30%'), (40, '40%'), (50, '50%'), (60, '60%'), (70, '70%'), (80, '80%'), (90, '90%'), (100, '100%')])
    PROGRESS_CHOICES = [
        (0, '0% progress'),
        (10, '10% progress'),
        (20, '20% progress'),
        (30, '30% progress'),
        (40, '40% progress'),
        (50, '50% progress'),
        (60, '60% progress'),
        (70, '70% progress'),
        (80, '80% progress'),
        (90, '90% progress'),
        (100, '100% completed')
    ]



    def __str__(self):
        return self.task_description

class TaskDeadlineUpdate(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    old_deadline = models.DateField()
    new_deadline = models.DateField()
    comment = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Update for {self.task.task_description} - New Deadline: {self.new_deadline}"

class UpdatedTask(models.Model):
    pass
# class Project(models.Model):
#     project_name = models.CharField(max_length=200)
#
#     def __str__(self):
#         return self.project_name


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



