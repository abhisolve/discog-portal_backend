# -*- coding: utf-8 -*-

from discomail.models import EmailQueue, PlatformInvite
from django.template.loader import render_to_string
from django.conf import settings


def send_invite_email(instance):
    """
    async function used by the PlarformInvite
    model post_save trigger. In order to send the email
    :instance <PlatformInvite model Instance>
    """
    body_string = render_to_string("discomail/user_invite_mail.html",
                                  context={'user': instance.user,
                                           'reset_password_hash': instance.invite_hash,
                                           'host': settings.HOST,
                                           'env': settings.ENV})
    email_queue_object = EmailQueue.objects.create(email_type="PJE",
                                                   subject="Discog LMS Invite",
                                                   body=body_string,
                                                   to_email=instance.user.email,)
    # Update the email_queue in
    # insance
    instance.email_queue = email_queue_object
    instance.save()

    # send the email using send_now
    # functionality
    email_queue_object.send_now = True
    email_queue_object.save()



def create_platform_invite_instance(instance, created):
    """
    Method used by DiscoUser post_save signal
    receiver. In order to generate an invite email
    for every user of the  application
    """
    if created:
        user_invite = PlatformInvite.objects.create(user=instance)
    else:
        pass
