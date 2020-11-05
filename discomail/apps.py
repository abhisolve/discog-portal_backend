# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.apps import AppConfig
from django.db.models.signals import post_save


class DiscomailConfig(AppConfig):
    name = 'discomail'
    verbose_name = 'Disco Mail'

    def ready(self):
        """
        connect models signals with
        handlers for the discomail sub
        application
        """
        from discomail.models import PlatformInvite, EmailQueue
        from discomail.signals.handlers import generate_email_queue, send_now_and_delete
        post_save.connect(generate_email_queue, sender=PlatformInvite, dispatch_uid="generate_email_queue")
        post_save.connect(send_now_and_delete, sender=EmailQueue, dispatch_uid="send_now_and_delete")
