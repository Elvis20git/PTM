# Generated by Django 5.0.4 on 2024-06-10 15:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('PTM', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='taskdeadlineupdate',
            name='impact_on_result',
            field=models.CharField(blank=True, choices=[('overdue_no_impact', 'Overdue - No impact on final result'), ('overdue_impact', 'Overdue - Impact on final result')], max_length=30, null=True),
        ),
    ]
