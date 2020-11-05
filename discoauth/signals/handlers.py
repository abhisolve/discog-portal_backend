# -*- coding: utf-8 -*-

from discogportal.discoutils.asyncutils import create_platform_invite_instance

def create_platform_invite(sender, instance, created, *args, **kwargs):
    if created:
        if instance.is_active == True:
            create_platform_invite_instance(instance, created)
        else:
            pass
    else:
        pass
