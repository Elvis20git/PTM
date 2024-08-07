# tasks.py
import threading
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.sites.models import Site
from urllib.parse import quote
from django.core.files.storage import default_storage
from PTM.models import CustomUser
from django.utils.html import strip_tags
from django.template.loader import render_to_string
import os

def async_send_project_email(usernames, project_name, project_file_path):
    # Debug information
    print(f"MEDIA_ROOT: {settings.MEDIA_ROOT}")
    print(f"MEDIA_URL: {settings.MEDIA_URL}")
    print(f"project_file_path: {project_file_path}")

    # Check file existence
    full_path = os.path.join(settings.MEDIA_ROOT, project_file_path)
    print(f"Full file path: {full_path}")
    print(f"File exists (os.path): {os.path.exists(full_path)}")
    print(f"File exists (default_storage): {default_storage.exists(project_file_path)}")

    # Get current site
    current_site = Site.objects.get_current()
    print(f"Current site domain: {current_site.domain}")

    # Construct file URL
    file_url = f"http://{current_site.domain}{settings.MEDIA_URL}{quote(project_file_path)}"
    print(f"Constructed file_url: {file_url}")

    # Construct email content
    subject = f'New Project Assigned: {project_name}'
    message = f'A new project "{project_name}" has been created and you have been tagged as a member.\n\n'

    if os.path.exists(full_path):
        message += f'You can download the project file using the following link:\n{file_url}'
    else:
        message += 'The project file is currently unavailable. Please contact the administrator.'

    email_from = settings.EMAIL_HOST_USER
    recipients = CustomUser.objects.filter(username__in=usernames).values_list('email', flat=True)

    # Debug: print recipients
    print(f"Recipients: {list(recipients)}")

    # Send email
    try:
        send_mail(subject, message, email_from, recipients)
        print("Email sent successfully")
    except Exception as e:
        print(f"Error sending email: {str(e)}")

    return file_url  # Return the file URL for further debugging if needed



def async_send_task_email(usernames, project_name, task_description, assigned_by, deadline):
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
        try:
            send_mail(subject, plain_message, email_from, [recipient], html_message=html_message, fail_silently=False)
            print(f"Task email sent successfully to {recipient}")
        except Exception as e:
            print(f"Error sending task email to {recipient}: {str(e)}")