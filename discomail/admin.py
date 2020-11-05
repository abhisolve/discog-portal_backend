# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from discomail.models import EmailLog, EmailQueue, PlatformInvite
# Register your models here.

admin.site.register(EmailQueue)
admin.site.register(EmailLog)
admin.site.register(PlatformInvite)
