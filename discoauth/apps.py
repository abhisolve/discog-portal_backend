# -*- coding: utf-8 -*-

from django.apps import AppConfig


class DiscoauthConfig(AppConfig):
    name = 'discoauth'
    verbose_name = "Disco Auth"

    def ready(self):
        # Activate the model triggers
        from django.db.models.signals import post_save
        from discoauth.models import DiscoUser
        from discoauth.signals.handlers import create_platform_invite

        post_save.connect(create_platform_invite, sender=DiscoUser)

