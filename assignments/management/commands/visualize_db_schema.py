# ./manage.py graph_models -a -g -o my.png
import os
from django.core.management.base import BaseCommand
from django.core import management
from django.conf import settings
from datetime import datetime
from django.db.models.signals import post_migrate


class Command(BaseCommand):
    help = 'Generates the DB schema, saves it in the visualized-db-schema directory with todays date'

    def handle(self, *args, **kwargs):
        management.call_command('graph_models', '--all-application', '--group-models', output=f"visualized-db-schema/{datetime.now().strftime('%d-%m-%Y')}.png")