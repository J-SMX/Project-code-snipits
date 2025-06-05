from django.db import models
from org.models import MenuItem


class Menu(models.Model):
    is_active = models.BooleanField(default=False)
    items = models.ManyToManyField(MenuItem)
