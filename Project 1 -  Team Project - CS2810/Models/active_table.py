from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from org.models import User
from django.utils import timezone


class ActiveTable(models.Model):
    # Primary key is table number
    table_number = models.DecimalField(default=-1, max_digits=3, decimal_places=0)
    # Number of seats at the table
    no_of_seats = models.DecimalField(default=0, decimal_places=0, max_digits=3, validators=[MaxValueValidator(100),
                                                                                             MinValueValidator(1)])
    timestamp_created = models.DateTimeField(editable=False)
    timestamp_destroyed = models.DateTimeField(editable=False, default=timezone.now)

    # Foreign key to point to waiter user, but no check required as this will be done when creating an active table
    # Requires blank=True, null=True to allow the field to be empty / null
    current_waiter = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
