# Generated by Django 5.0.4 on 2024-07-08 13:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('PTM', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='task',
            old_name='assign_to',
            new_name='assigned_to',
        ),
    ]
