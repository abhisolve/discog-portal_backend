# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.conf import settings
from discoauth.models import DiscoUser, random_invite_hash
# Create your models here.


class EmailQueue(models.Model):
    EMAIL_TYPE_CHOICES = (('FPE', "Forgot Password Email"),
                          ('PJE', "Platform Joining Email"))
    EMAIL_STATUS_CHOICES = (('SUC', "Success"),
                            ('ERR', "Error"),
                            ('NA', "Not Available"))
    email_type = models.CharField(max_length=3, choices=EMAIL_TYPE_CHOICES, default="FPE")
    email_status = models.CharField(max_length=3, choices=EMAIL_STATUS_CHOICES, default="NA")
    subject = models.CharField(max_length=255)
    body = models.TextField()
    to_email = models.CharField(max_length=255)
    from_email = models.CharField(max_length=255, default=settings.FROM_EMAIL)
    email_server_response_text = models.TextField(null=True, blank=True)
    send_now = models.BooleanField(default=False)

    def __str__(self):
        return "%s - %s" % (self.to_email, self.subject)

    @property
    def failed_attempts(self):
        """
        Total failed attempats of sending this email
        """
        return self.email_logs.filter(email_status="ERR").count()



class EmailLog(models.Model):
    """
    Model used to store the logs of the mails send
    and mails discarded.
    """
    EMAIL_TYPE_CHOICES = (('FPE', "Forgot Password Email"),
                          ('PJE', "Platform Joining Email"))
    EMAIL_STATUS_CHOICES = (('SUC', "Success"),
                            ('ERR', "Error"),
                            ('NA', 'Not Available'))
    email_queue = models.ForeignKey(EmailQueue, null=True, blank=True, on_delete=models.SET_NULL, related_name="email_logs")
    email_type = models.CharField(max_length=3, choices=EMAIL_TYPE_CHOICES, default="FPE")
    email_status = models.CharField(max_length=3, choices=EMAIL_STATUS_CHOICES, default="NA")
    subject = models.CharField(max_length=255)
    body = models.TextField()
    to_email = models.CharField(max_length=255)
    email_server_response_text = models.TextField(null=True, blank=True)
    from_email = models.CharField(max_length=255, default=settings.FROM_EMAIL)

    def __str__(self):
        return "%s - %s" % (self.to_email, self.subject)

    def clean(self):
        """
        An Error status EmailLog Doesn't exist without an 
        """
        super(EmailQueue, self).clean()
        if self.email_status == "ERR" and self.email_queue is None:
            raise ValidateionError({"email_queue": "For Error Type Email Logs Email Queue Is Required"})


class PlatformInvite(models.Model):
    """
    model to store the User invites to
    this platform
    """
    user = models.OneToOneField(DiscoUser, related_name="platform_invite", on_delete=models.CASCADE)
    invite_hash = models.CharField(max_length=255, default=random_invite_hash)
    email_log = models.OneToOneField(EmailLog, related_name="platform_invite", on_delete=models.SET_NULL, null=True, blank=True)
    email_queue = models.OneToOneField(EmailQueue, related_name="platform_invite", on_delete=models.SET_NULL, null=True, blank=True)
    used = models.BooleanField(default=False)
    used_on_datetime = models.DateTimeField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "#%s - %s - %s" % (self.id, self.user.id, self.invite_hash)

    class Meta:
        verbose_name = "Platform Invite"
        verbose_name_plural = "Platform Invites"
