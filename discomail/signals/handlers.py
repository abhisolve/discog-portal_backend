# -*- coding: utf-8 -*-

from discogportal.discoutils.asyncutils import send_invite_email
from django.core.mail import EmailMessage
from django.conf import settings
from discomail.models import EmailLog


def generate_email_queue(sender, instance, created,  *args,  **kwargs):
    """
    Generate Email queue object, save it
    and trigger send opration on that
    """
    if created:
        send_invite_email(instance)
    else:
        pass
    

def send_now_and_delete(sender, instance, *args, **kwargs):
    """
    send emails instantly if send_now=True 
    and then delete the instance after creating
    a log if mail has sent successfuly othewise
    don't delete the instance but create an Error
    Type log.
    """
    if(instance.send_now):
        email_message = EmailMessage(instance.subject,
                                     instance.body,
                                     instance.from_email,
                                     [instance.to_email, ],
                                     bcc=settings.BCC_EMAILS)
        email_message.content_subtype = 'html'
        mail_sent = email_message.send(fail_silently=False)
        if(mail_sent == 1):
            email_log = EmailLog.objects.create(email_type=instance.email_type,
                                                email_status="SUC",
                                                from_email=instance.from_email,
                                                subject = instance.subject,
                                                body = instance.body,
                                                to_email = instance.to_email)
            if hasattr(instance, 'platform_invite'):
                # if platform invite exists.
                # we need to update the the email_log
                # in it too as we need to make sure
                # that we have accurate history of all
                # invites.
                platform_invite = instance.platform_invite
                platform_invite.email_log = email_log
                platform_invite.save()
            else:
                pass
            instance.delete()
        else:
            instance.email_status = "ERR"
            instance.send_now = False
            instance.save()
            email_log = EmailLog.objects.create(email_type=instance.email_type,
                                                email_status="ERR",
                                                email_queue=instance,
                                                from_email=instance.from_email,
                                                subject = instance.subject,
                                                body = instance.body,
                                                to_email = instance.to_email)
            if hasattr(instance, 'platform_invite'):
                # if platform invite exists.
                # we need to update the the email_log
                # in it too as we need to make sure
                # that we have accurate history of all
                # invites.
                platform_invite = instance.platform_invite
                platform_invite.email_log = email_log
                platform_invite.save()
            else:
                pass
    else:
        pass
