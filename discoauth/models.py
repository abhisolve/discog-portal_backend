# -*- coding: utf-8 -*-

import os
from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from phonenumber_field.modelfields import PhoneNumberField
from simple_history.models import HistoricalRecords
from django.utils import timezone
from django.contrib.auth.models import PermissionsMixin
from django.core.exceptions import ValidationError
from django.db.models.signals import pre_save
from django.dispatch import receiver
import random
import string
from django.conf import settings
import binascii


def determine_user_profile_photo_directory(instance, filename):
    return f'user_profile_photo/{instance.id}/{filename}'


def random_invite_hash():
    """
    generate a ramdom string
    for user invites
    """
    return ''.join(random.choice(string.ascii_lowercase) for i in range(25))


def randomString(stringLength=4):
    """
    helper function to generate the random string
    which will be added to as staff_id in staff details model
    """
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))



class DiscoUserManager(BaseUserManager):
    def create_user(self, email, password):
        """
        Creates and saves a User with the given email, username and password.
        """
        if not email:
            raise ValueError('Users must have an email address')
        if not password:
            raise ValueError('Password is required')

        user = self.model(
            email=self.normalize_email(email),
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        """
        Creates and saves a User with the given email, username and password.
        """
        user = self.create_user(
            email=email,
            password=password,
        )
        user.is_staff = True
        user.is_teacher = True
        user.save(using=self._db)
        # generate a staff detail with random ID
        from assignments.models import StaffDetail
        StaffDetail.objects.create(staff_id="STF-%s" %(randomString()),
                                   user=user,
                                   staff_role='MAN')
        return user


class PasswordReset(models.Model):
    is_active = models.BooleanField(default=True)
    reset_request_date = models.DateTimeField(auto_now=True)
    reset_request_successful = models.DateTimeField(null=True, blank=True)
    reset_request_valid_till = models.DateTimeField(null=True, blank=True)
    password_hash = models.CharField(max_length=255)
    user = models.ForeignKey('discouser', null=True, blank=True, on_delete=models.CASCADE, related_name='password_resets')

    def __str__(self):
        if self.user:
            return "%s %s " % (self.user.username, self.password_hash)  # NOQA
        else:
            return "None %s" % (self.password_hash)

    class Meta:
        verbose_name = 'Password Reset'
        verbose_name_plural = 'Password Resets'

    def save(self, *args, **kwargs):
        now = timezone.now()
        additional_time = timezone.timedelta(hours=6)
        self.reset_request_valid_till=now+additional_time
        super(PasswordReset, self).save(*args, **kwargs)


class Parent(models.Model):
    """
    Model used to store the parent infromation
    of the DiscoUser for whom is_student is checked
    """
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    parent_id = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return "%s-%s-%s" % (self.id, self.parent_id, self.email)

    class Meta:
        verbose_name = "Parent"
        verbose_name_plural = "Parents"


class DiscoUser(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
    )
    username = models.CharField(max_length=255, unique=True, null=True, blank=True)
    phone_number = PhoneNumberField(null=True, blank=True)
    profile_photo = models.FileField(upload_to=determine_user_profile_photo_directory, null=True, blank=True)
    parent = models.ForeignKey(Parent,
                               related_name="childrens",
                               on_delete=models.CASCADE,
                               null=True,
                               blank=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_student = models.BooleanField(default=False)
    is_teacher = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = DiscoUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

    def clean(self):
        if self.is_student and self.parent is  None:
            raise ValidationError({'parent': "Parent is required field for students"})
        elif not self.is_student and self.parent is not None:
            raise ValidationError({'parent': "Only Students are allowed to have parents"})
        super(DiscoUser, self).clean()

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def isteacher(self):
        return self.is_teacher

    @property
    def isstudent(self):
        return self.is_student


    @property
    def student_id(self):
        if self.is_student and self.student_detail:
            return self.student_detail.roll_number
        else:
            return None

    @property
    def student_type(self):
        if self.is_student and self.student_detail:
            return self.student_detail.student_type
        else:
            return None

@receiver(pre_save, sender=DiscoUser, dispatch_uid="inactive_to_active")
def inactive_to_active(sender, instance, **kwargs):

    """
    Pre save triiger to check user status change from inactive to active
    and then call the platform invite email method to send the invite email
    to the user.
    """

    if instance.is_active and DiscoUser.objects.filter(id=instance.id, is_active=False).exists():
        from discogportal.discoutils.asyncutils import create_platform_invite_instance
        from discomail.models import PlatformInvite
        if not PlatformInvite.objects.filter(user=instance).exists():
            created = True
            create_platform_invite_instance(instance, created)
        else:
            pass
    else:
        pass
