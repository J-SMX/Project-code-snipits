from django.db import models

from org.models import MenuItem, OrderStatusChoices, PaymentStatusChoices, User, DiscountCode, Payment


class HistoricalOrder(models.Model):
    id = models.BigIntegerField(primary_key=True)
    timestamp_ordered = models.DateTimeField(editable=False)
    timestamp_completed = models.DateTimeField(editable=False, auto_now_add=True)
    items_selected = models.ManyToManyField(MenuItem)
    final_price_ex_vat = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    final_price_inc_vat = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    order_status = models.CharField(choices=OrderStatusChoices.choices, max_length=2)
    payment_status = models.CharField(choices=PaymentStatusChoices.choices, max_length=2)

    # N.B.: For testing purposes, these fields will be made nullable. This should not be the case when development has
    # finished. TODO: Remove blank=True, null=True from these fields
    customer = models.ForeignKey(User, related_name="historicalorder_customer_set", on_delete=models.PROTECT,
                                 blank=True, null=True)
    waiter = models.ForeignKey(User, related_name="historicalorder_waiter_set", on_delete=models.PROTECT, blank=True,
                               null=True)
    payment_id = models.ForeignKey(Payment, on_delete=models.PROTECT, blank=True, null=True)
    discount_id = models.ForeignKey(DiscountCode, on_delete=models.PROTECT, blank=True, null=True)
