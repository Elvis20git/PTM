from django.conf import settings
from django.contrib.sites.models import Site
from urllib.parse import quote
import threading
from .tasks import async_send_project_email
from .tasks import async_send_task_email

def send_project_email(usernames, project_name, project_file_path):
    # Start a new thread for sending email
    thread = threading.Thread(
        target=async_send_project_email,
        args=(usernames, project_name, project_file_path)
    )
    thread.start()

    # Construct and return the file URL (if you need it immediately)
    current_site = Site.objects.get_current()
    file_url = f"http://{current_site.domain}{settings.MEDIA_URL}{quote(project_file_path)}"

    print(f"Email task started in a new thread")
    return file_url


def send_task_email(usernames, project_name, task_description, assigned_by, deadline):
    # Start a new thread for sending email
    thread = threading.Thread(
        target=async_send_task_email,
        args=(usernames, project_name, task_description, assigned_by, deadline)
    )
    thread.start()

    print(f"Task email sending started in a new thread")