# Generated by Django 5.0.4 on 2024-07-30 16:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('PTM', '0007_task_user_task_file'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='department',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
