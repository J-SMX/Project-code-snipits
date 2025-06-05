from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from org.models.item_type import ItemType



def validate_allergen(value):
    allergens_list = value.split(",")
    for item in allergens_list:
        try:
            if int(item) > 14 or int(item) < 1:
                raise ValidationError(_('%(value)s out of range - should be between 1 and 14'), params={'value': value})
        except ValueError:
            raise ValidationError(_('%(value)s is not a number in the range 1-14'), params={'value': value})


class MenuItem(models.Model):
    item_name = models.CharField(max_length=255)
    item_description = models.CharField(default="", max_length=255)
    item_type = models.ForeignKey(ItemType, on_delete=models.DO_NOTHING, blank=True, null=True)
    price_ex_vat = models.DecimalField(default=-1, max_digits=5, decimal_places=2)
    price_inc_vat = models.DecimalField(default=-1, max_digits=5, decimal_places=2)
    # vat_percentage should be a number between 1-100
    vat_percentage = models.DecimalField(default=0, max_digits=3, validators=[MaxValueValidator(100), MinValueValidator(0)], decimal_places=0)

    # There are 14 allergens, so for each allergen we could store it as a number 1-14, and just have a list of those
    # numbers, comma-separated. For example, if there were the three allergens 2, 4 and 5 in the item, the
    # allergens_numbers would be 2,4,5
    # That means the theoretical maximum length of this field is 1,2,3,4,5,6,7,8,9,10,11,12,13,14
    # which is a total of 32 characters
    allergens_numbers = models.CharField(default="", max_length=32, validators=[validate_allergen])

    is_available = models.BooleanField(default=True)
    picture = models.ImageField(upload_to ='uploads/', null=True, blank=True)