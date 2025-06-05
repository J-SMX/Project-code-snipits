from django.db import models
from django.utils.translation import gettext_lazy as _


class OrderStatusChoices(models.TextChoices):
    PLACED = "PL", _("Placed")

    # Orders must be confirmed by the assigned waiter before they are sent to the kitchen.
    CONFIRMED = "CN", _("Confirmed")

    # Orders can be updated by the customer by adding additional menu items.
    UPDATED = "UD", _("Updated")

    # An order is ready when all the items have been made by the kitchen.
    READY = "RD", _("Ready")

    # An order is fulfilled when all the items have been delivered to the customer.
    FULFILLED = "FF", _("Fulfilled")

    CANCELLED = "CC", _("Cancelled")


class PaymentStatusChoices(models.TextChoices):
    # The payment_status field is used to store the status of the payment
    PAID = "P", _("Paid")
    UNPAID = "UP", _("Unpaid")
    REFUNDED = "R", _("Refunded")
    PARTIALLY_REFUNDED = "PR", _("Partially Refunded")
