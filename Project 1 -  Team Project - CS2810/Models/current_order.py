from django.core.exceptions import ValidationError
from django.db import models
from org.models import MenuItem, PaymentStatusChoices, OrderStatusChoices, User, Payment, DiscountCode
from django.utils.translation import gettext_lazy as _
from decimal import Decimal


def customer_validator(value):
    if not value.groups.filter(name='customer').exists():
        raise ValidationError(_("%(value) is not a customer", params={"value": value}))


def waiter_validator(value):
    if not value.groups.filter(name='waiter').exists():
        raise ValidationError(_("%(value) is not a waiter", params={"value": value}))


class CurrentOrder(models.Model):
    timestamp_ordered = models.DateTimeField(editable=False, auto_now_add=True)
    items_selected = models.ManyToManyField(MenuItem, related_name="currentorder_selected_set")
    items_fulfilled = models.ManyToManyField(MenuItem, related_name="currentorder_fulfilled_set", blank=True)
    final_price_ex_vat = models.DecimalField(default=None, max_digits=5, decimal_places=2, null=True, blank=True)
    final_price_inc_vat = models.DecimalField(default=None, max_digits=5, decimal_places=2, null=True, blank=True)
    order_status = models.CharField(
        choices=OrderStatusChoices.choices,
        default=OrderStatusChoices.PLACED,
        max_length=2,
    )
    payment_status = models.CharField(
        choices=PaymentStatusChoices.choices,
        default=PaymentStatusChoices.UNPAID,
        max_length=2,
    )
    customer = models.ForeignKey(User, related_name="currentorder_customer_set", on_delete=models.PROTECT, validators=[customer_validator], blank=True, null=True)
    waiter = models.ForeignKey(User, related_name="currentorder_waiter_set", on_delete=models.PROTECT, validators=[waiter_validator], blank=True, null=True)

    # XXX
    payment_id = models.ForeignKey(Payment, on_delete=models.PROTECT, blank=True, null=True)
    discount_id = models.ForeignKey(DiscountCode, on_delete=models.PROTECT, blank=True, null=True)

    def apply_discount(self, discount_code):
        # this checks if discount_code is a DiscountCode, raising an error if not
        if not isinstance(discount_code, DiscountCode):
            raise ValueError('Discount code not applicable to order')
        # this validates if the discount code is active and therefore valid
        if not discount_code.active:
            raise ValueError('Discount code is not active')

        # this validates that there are applicable items
        num_applicable_items = len(discount_code.applicable_items.all())
        if num_applicable_items == 0:
            raise ValueError('No applicable items')

        self.discount_id = discount_code

        discount_value = Decimal('0')
        for item in self.items_selected.all():
            if item in discount_code.applicable_items.all():
                discount_value += item.price_ex_vat * discount_code.discount_percentage / 100

        self.final_price_ex_vat = Decimal(self.final_price_ex_vat) - discount_value
        self.final_price_inc_vat = Decimal(self.final_price_inc_vat) - discount_value * (
                    100 + self.discount_id.discount_percentage) / 100
        self.save()

    def mark_as_paid(self):
        if self.payment_status == "UP":
            self.status = "P"
            self.save()
        else:
            raise ValueError("Order is not in unpaid status.")

    def confirm_order(self):
        self.order_status = "CN"
        self.save()

