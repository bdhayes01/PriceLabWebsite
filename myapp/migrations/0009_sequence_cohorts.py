# Generated by Django 4.2.16 on 2024-09-18 17:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0008_remove_sequence_individual_remove_sequence_sequence'),
    ]

    operations = [
        migrations.AddField(
            model_name='sequence',
            name='Cohorts',
            field=models.JSONField(default=dict),
        ),
    ]
