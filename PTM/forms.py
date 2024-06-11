from allauth.account.forms import SignupForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import UserManager
from django.db import models
from django import forms
from .models import Meeting, MeetingNote, TaskDeadlineUpdate, CustomUser
from django.utils import timezone
from django.contrib.auth.forms import UserChangeForm


class MeetingForm(forms.ModelForm):
    class Meta:
        model = Meeting
        fields = ['project', 'meeting_date', 'meeting_time']
        widgets = {
            'project': forms.Select(attrs={'class': 'form-select'}),
            'meeting_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'meeting_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            # 'notes': forms.Textarea(attrs={'id': 'meeting-notes'}),
        }

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

# class CustomSignupForm(SignupForm):
#     first_name = forms.CharField(max_length=30, label='First Name')
#     last_name = forms.CharField(max_length=30, label='Last Name')
#     activate = forms.BooleanField(label='Activate Account', required=False)
#
#     def __init__(self, *args, **kwargs):
#         super(CustomSignupForm, self).__init__(*args, **kwargs)
#         self.fields['username'].widget.attrs.update({'class': 'form-control'})
#         self.fields['email'].widget.attrs.update({'class': 'form-control'})
#         self.fields['password1'].widget.attrs.update({'class': 'form-control'})
#         self.fields['password2'].widget.attrs.update({'class': 'form-control'})
#         self.fields['first_name'].widget.attrs.update({'class': 'form-control'})
#         self.fields['last_name'].widget.attrs.update({'class': 'form-control'})
#         self.fields['activate'].widget.attrs.update({'class': 'form-check-input'})
#
#     def save(self, request):
#         user = super(CustomSignupForm, self).save(request)
#         user.first_name = self.cleaned_data['first_name']
#         user.last_name = self.cleaned_data['last_name']
#         user.is_active = False  # Deactivate account until it is activated by an admin
#         user.save()
#         return user

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
        self.fields['username'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Username'})
        self.fields['full_name'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Full Name'})
        self.fields['phone_number'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Phone Number'})
        self.fields['email'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Email'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Password'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Confirm Password'})
        self.fields['account_activation'].widget.attrs.update({'class': 'form-check-input'})
        self.fields['role'].widget.attrs.update({'class': 'form-select'})

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'full_name', 'phone_number', 'email', 'account_activation')