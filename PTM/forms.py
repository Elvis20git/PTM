from allauth.account.forms import SignupForm
from django.conf import settings
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import UserManager
from django.core.mail import send_mail
from django.db import models
from django import forms
from .models import Meeting, MeetingNote, TaskDeadlineUpdate, CustomUser, Allprojects
from django.utils import timezone
from django.contrib.auth.forms import UserChangeForm
import secrets
import string


class MeetingForm(forms.ModelForm):
    class Meta:
        model = Meeting
        fields = ['project', 'meeting_date', 'meeting_time']
        widgets = {
            'project': forms.Select(attrs={'class': 'form-select'}),
            'meeting_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'meeting_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        projects = kwargs.pop('projects', None)
        super().__init__(*args, **kwargs)  # Corrected this line
        if projects is not None:
            self.fields['project'].queryset = projects
        else:
            self.fields['project'].queryset = Allprojects.objects.none()

class MeetingNoteForm(forms.ModelForm):
    class Meta:
        model = MeetingNote
        fields = ['note_type', 'note_content', 'decided_by', 'assigned_to', 'assigned_by', 'deadline_date']
        widgets = {
            'note_type': forms.Select(attrs={'id': 'note-type-dropdown', 'class': 'form-select'}),
            'note_content': forms.Textarea(attrs={'id': 'editor', 'class': 'form-control'}),
            'decided_by': forms.TextInput(attrs={'id': 'decided-by', 'class': 'form-control'}),
            'assigned_to': forms.TextInput(attrs={'id': 'assigned-to', 'class': 'form-control'}),
            'assigned_by': forms.TextInput(attrs={'id': 'assigned-by', 'class': 'form-control'}),
            'deadline_date': forms.DateInput(attrs={'type': 'date', 'id': 'deadline-date', 'class': 'form-control'}),
        }
class TaskDeadlineUpdateForm(forms.ModelForm):
    class Meta:
        model = TaskDeadlineUpdate
        fields = ['old_deadline', 'new_deadline', 'impact_on_result', 'comment']
        widgets = {
            'old_deadline': forms.DateInput( attrs={'readonly': 'readonly', 'class': 'form-control'}),
            'new_deadline': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'impact_on_result': forms.Select(attrs={'id': 'impact_on_result', 'class': 'form-control'}),
            'comment': forms.Textarea(attrs={'id': 'editor', 'class': 'form-control', 'rows': 3, 'required': 'required'}),

        }

    def save(self, commit=True):
        instance = super().save(commit=False)
        if not instance.timestamp:
            instance.timestamp = timezone.now()
        if commit:
            instance.save()
        return instance



class CustomUserCreationForm(UserCreationForm):
    full_name = forms.CharField(max_length=30, label='First Name')
    phone_number = forms.CharField(max_length=30, label='Phone Number')
    email = forms.EmailField(label='Email')
    account_activation = forms.BooleanField(required=False, label='Account Activation')
    role = forms.ChoiceField(choices=[('admin', 'Admin'), ('manager', 'Manager'), ('user', 'User')], label='Role')

    class Meta:
        model = CustomUser
        fields = ['username', 'full_name', 'phone_number', 'email', 'password1', 'password2', 'account_activation', 'role']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        random_password = self.generate_random_password()
        self.random_password = random_password  # Store the generated password
        self.fields['password1'].initial = random_password
        self.fields['password2'].initial = random_password

        self.fields['username'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Username'})
        self.fields['full_name'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Full Name'})
        self.fields['phone_number'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Phone Number'})
        self.fields['email'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Email'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Password', 'value': random_password})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Confirm Password', 'value': random_password})
        self.fields['account_activation'].widget.attrs.update({'class': 'form-check-input'})
        self.fields['role'].widget.attrs.update({'class': 'form-select'})

    @staticmethod
    def generate_random_password(length=12):
        characters = string.ascii_letters + string.digits + string.punctuation
        return ''.join(secrets.choice(characters) for _ in range(length))

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.random_password)  # Set the user's password to the generated one
        if commit:
            user.save()
            self.send_password_email(user)
        return user

    def send_password_email(self, user):
        subject = 'Your Account Credentials'
        message = f'Hello {user.username},\n\nYour account has been created. Your login credentials are:\nUsername: {user.username}\nPassword: {self.random_password}\n\nPlease change your password after logging in.'
        from_email = 'dev.team@africaimprovedfoods.com'
        recipient_list = [user.email]
        send_mail(subject, message, from_email, recipient_list)

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'full_name', 'phone_number', 'email', 'account_activation')


