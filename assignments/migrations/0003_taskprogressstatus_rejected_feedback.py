# Generated by Django 3.0.5 on 2020-09-02 09:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assignments', '0002_auto_20200731_1055'),
    ]

    operations = [
        migrations.AddField(
            model_name='taskprogressstatus',
            name='rejected_feedback',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
