from django.core.mail import send_mail
from django.conf import settings
from .models import CustomUser

def send_project_email(usernames, project_name):
    subject = 'New Project Created'
    message = f'A new project "{project_name}" has been created and you have been tagged as a member.'
    email_from = settings.EMAIL_HOST_USER
    recipients = CustomUser.objects.filter(username__in=usernames).values_list('email', flat=True)
    send_mail(subject, message, email_from, recipients)