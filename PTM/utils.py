from django.core.mail import send_mail
from django.conf import settings
from django.utils.html import strip_tags

from .models import CustomUser
from django.template.loader import render_to_string
def send_project_email(usernames, project_name):
    subject = f'New Project Assigned: {project_name}'
    message = f'A new project "{project_name}" has been created and you have been tagged as a member.'
    email_from = settings.EMAIL_HOST_USER
    recipients = CustomUser.objects.filter(username__in=usernames).values_list('email', flat=True)
    send_mail(subject, message, email_from, recipients)

# def send_task_email(usernames, project_name, task_description):
#     subject = f'New Task Assigned: {project_name}, {task_description}'
#     message = f'A new Task "{task_description}" has been assigned to you.'
#     email_from = settings.EMAIL_HOST_USER
#     recipients = CustomUser.objects.filter(username__in=usernames).values_list('email', flat=True)
#     send_mail(subject, message, email_from, recipients)


def send_task_email(usernames, project_name, task_description, assigned_by, deadline):
    subject = f'New Task Assigned: {project_name}'
    email_from = settings.EMAIL_HOST_USER
    recipients = CustomUser.objects.filter(username__in=usernames).values_list('email', flat=True)

    for recipient in recipients:
        html_message = render_to_string('PTM/task_email_template.html', {
            'task_description': task_description,
            'project_name': project_name,
            'assigned_by': assigned_by,
            'deadline': deadline,
            'recipient': recipient,
        })
        plain_message = strip_tags(html_message)  # Convert HTML to plain text
        send_mail(subject, plain_message, email_from, [recipient], html_message=html_message, fail_silently=False)

