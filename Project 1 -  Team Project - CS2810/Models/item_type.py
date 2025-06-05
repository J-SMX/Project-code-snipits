from django.db import models


class ItemType(models.Model):
    name = models.CharField(max_length=255)
    description = models.CharField(default="", max_length=255)
    parent = models.ForeignKey("self", on_delete=models.CASCADE, blank=True, null=True)
