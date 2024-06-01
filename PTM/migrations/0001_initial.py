# Generated by Django 5.0.4 on 2024-06-01 13:05

import django.contrib.auth.models
import django.contrib.auth.validators
import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Allprojects',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('project_name', models.CharField(max_length=100)),
                ('project_manager', models.CharField(max_length=100)),
                ('ProjectM_tags', models.JSONField(default=list)),
            ],
        ),
        migrations.CreateModel(
            name='MyModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tags', models.JSONField()),
            ],
        ),
        migrations.CreateModel(
            name='UpdatedTask',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='Meeting',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('meeting_date', models.DateField(blank=True, null=True)),
                ('meeting_time', models.TimeField(blank=True, null=True)),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='meetings', to='PTM.allprojects')),
            ],
        ),
        migrations.CreateModel(
            name='MeetingNote',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('note_type', models.CharField(blank=True, choices=[('note', 'Note'), ('decision', 'Decision'), ('action', 'Action')], max_length=10, null=True)),
                ('note_content', models.TextField(blank=True, null=True)),
                ('decided_by', models.CharField(blank=True, max_length=200, null=True)),
                ('assigned_to', models.CharField(blank=True, max_length=200, null=True)),
                ('assigned_by', models.CharField(blank=True, max_length=200, null=True)),
                ('deadline_date', models.DateField(blank=True, null=True)),
                ('meeting', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='meeting_notes', to='PTM.meeting')),
            ],
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('task_description', models.CharField(max_length=255)),
                ('assign_to', models.CharField(max_length=100)),
                ('deadline', models.DateField()),
                ('completion_date', models.DateField(blank=True, null=True)),
                ('assigned_by', models.CharField(max_length=100)),
                ('status', models.IntegerField(choices=[(1, 'Open'), (2, 'Completed'), (3, 'In Progress'), (4, 'Overdue')], default=1)),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='PTM.allprojects')),
            ],
        ),
        migrations.CreateModel(
            name='TaskDeadlineUpdate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('old_deadline', models.DateField()),
                ('new_deadline', models.DateField()),
                ('comment', models.TextField()),
                ('timestamp', models.DateTimeField(default=django.utils.timezone.now)),
                ('task', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='PTM.task')),
            ],
        ),
        migrations.CreateModel(
            name='CustomUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('full_name', models.CharField(max_length=100)),
                ('phone_number', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('account_activation', models.BooleanField(default=False)),
                ('role', models.CharField(choices=[('admin', 'Admin'), ('manager', 'Manager'), ('user', 'User')], default='user', max_length=20)),
                ('groups', models.ManyToManyField(blank=True, related_name='customuser_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, related_name='customuser_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
    ]
