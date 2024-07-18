import datetime
from django.core.management.base import BaseCommand
from django.utils import timezone
from PTM.models import Task
from PTM.utils import send_notification  # Import the internal notification function

class Command(BaseCommand):
    help = 'Check tasks for upcoming due dates and overdue status'

    def handle(self, *args, **kwargs):
        today = timezone.now().date()
        three_days_later = today + datetime.timedelta(days=3)

        # Check for tasks due in 3 days
        upcoming_tasks = Task.objects.filter(deadline=three_days_later, status__in=[1, 3])  # Adjust status values as needed

        for task in upcoming_tasks:
            user = task.assigned_to
            send_notification(user, f'Task "{task.task_description}" is due in 3 days.')

        # Check for overdue tasks
        overdue_tasks = Task.objects.filter(deadline__lt=today, status__in=[1, 3])  # Adjust status values as needed

        for task in overdue_tasks:
            task.status = 4  # Assuming status 4 is 'Overdue'
            task.save()
            user = task.assigned_to
            send_notification(user, f'Task "{task.task_description}" is now overdue.')

        self.stdout.write(self.style.SUCCESS('Successfully checked tasks for due dates and overdue status.'))