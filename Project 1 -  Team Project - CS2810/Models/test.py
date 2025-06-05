from django.db import models


class TestModel(models.Model):
    # Example columns for the purpose of testing

    nameTest = models.CharField(max_length=255)
    ageTest = models.IntegerField()
    numMenuItemsTest = models.IntegerField()
