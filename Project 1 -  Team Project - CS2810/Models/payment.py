from django.db import models


class Payment(models.Model):
    verification_token = models.CharField(max_length=255, blank=False, default=0)
