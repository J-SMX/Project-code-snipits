from django.db import models
from org.models import MenuItem


class DiscountCode(models.Model):
    active = models.BooleanField(default=True, blank=False)
    discount_name = models.CharField(max_length=32, blank=False)
    discount_percentage = models.DecimalField(default=0, max_digits=5, decimal_places=2)
    discount_value = models.DecimalField(default=0, max_digits=5, decimal_places=2)
    applicable_items = models.ManyToManyField(MenuItem)
