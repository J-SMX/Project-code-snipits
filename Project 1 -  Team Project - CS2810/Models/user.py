from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import AbstractUser
import re
from django.utils.translation import gettext_lazy as _

from django.contrib.auth.models import Group


# performs validation on an inputted email address
def email_validation(value):
    # regular expression used to define an email addreess
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    if not re.fullmatch(regex, value):
        raise ValidationError(_('%(value) is not a valid email address'), params={'value': value})


# performs validation on an inputted first/last name
def name_validation(value):
    # regular expression used to define a first/last name
    regex = r'^[A-Z][a-z]*$'
    if not re.fullmatch(regex, value):
        raise ValidationError(_('%(value) is not a valid \'first\' or \'last\' name'), params={'value': value})


class User(AbstractUser):
    # Extend the auth_user model to force the email address to be used for the username
    email = models.EmailField(max_length=254, blank=False, unique=True, validators=[email_validation])
    first_name = models.CharField(max_length=32, blank=False, validators=[name_validation])
    last_name = models.CharField(max_length=32, blank=False, validators=[name_validation])
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    groups = models.ManyToManyField(Group)


"""class Users(models.Model):
    username = models.CharField(max_length=255, blank=False)
    password = models.CharField(max_length=255, blank=False)
    email = models.CharField(max_length=255, blank=False, validators=[email_validation])
    forename = models.CharField(max_length=32, blank=False, validators=[name_validation])
    surname = models.CharField(max_length=32, blank=False, validators=[name_validation])
    last_login = models.DateTimeField(auto_now_add=True)
"""
