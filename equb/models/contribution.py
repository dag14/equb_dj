import uuid
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from decimal import Decimal
from .group import EqubGroup, GroupMember


class Contribution(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable= False)
    STATUS_PENDING = "pending"
    STATUS_PAID = "paid"
    STATUS_LATE = "late"
    STATUS_MISSED = "missed"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_PAID, "Paid"),
        (STATUS_LATE, "Late"),
        (STATUS_MISSED, "Missed"),
    ]

    group = models.ForeignKey(
        EqubGroup,
        on_delete=models.CASCADE,
        related_name="contributions"
    )
    member = models.ForeignKey(
        GroupMember,
        on_delete=models.CASCADE,
        related_name="contributions"
    )
    cycle_number = models.PositiveIntegerField(
        help_text="Which payout cycle this contribution belongs to."
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="The contribution amount for this cycle."
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING
    )
    payment_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the payment was actually made."
    )
    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="recorded_contributions",
        help_text="User who recorded this payment, if applicable."
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["member", "cycle_number"], name="unique_member_cycle")
        ]
        ordering = ["group", "cycle_number", "member"]

    def __str__(self):
        return f"{self.member.user.username} - Cycle {self.cycle_number} - {self.status}"

    def clean(self):
        if self.amount <= Decimal('0'):
            raise ValidationError("Contribution amount must be a positive number.")
        if self.group and self.amount != self.group.contribution_amount:
            raise ValidationError(
                f"Contribution amount ({self.amount}) does not match group's contribution_amount ({self.group.contribution_amount})."
            )
        if self.member.group_id != self.group_id:
            raise ValidationError("Contribution member must belong to the contribution group.")
        if self.cycle_number > self.group.total_cycles:
            raise ValidationError(f"Cycle number {self.cycle_number} exceeds total cycles {self.group.total_cycles}.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class PayoutSchedule(models.Model):
    id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    STATUS_SCHEDULED = "scheduled"
    STATUS_PAID = "paid"
    STATUS_DELAYED = "delayed"
    STATUS_SKIPPED = "skipped"

    STATUS_CHOICES = [
        (STATUS_SCHEDULED, "Scheduled"),
        (STATUS_PAID, "Paid"),
        (STATUS_DELAYED, "Delayed"),
        (STATUS_SKIPPED, "Skipped"),
    ]

    group = models.ForeignKey(
        EqubGroup,
        on_delete=models.CASCADE,
        related_name="payout_schedules"
    )
    recipient = models.ForeignKey(
        GroupMember,
        on_delete=models.CASCADE,
        related_name="payout_schedules"
    )
    cycle_number = models.PositiveIntegerField(
        help_text="Cycle number matching the contribution cycle."
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Total payout amount for this cycle."
    )
    scheduled_date = models.DateField(
        help_text="Planned payout date for this cycle."
    )
    actual_date = models.DateField(
        null=True,
        blank=True,
        help_text="The date payout was actually made."
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default=STATUS_SCHEDULED
    )
    notes = models.TextField(
        null=True,
        blank=True,
        help_text="Optional notes about payout delays or special cases."
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["group", "cycle_number"], name="unique_group_cycle_payout")
        ]
        ordering = ["group", "cycle_number"]

    def __str__(self):
        return f"Payout Cycle {self.cycle_number} for {self.recipient.user.username}"

    def clean(self):
        if self.recipient.group_id != self.group_id:
            raise ValidationError("Payout recipient must be a member of the payout group.")
        if self.cycle_number > self.group.total_cycles:
            raise ValidationError(f"Cycle number {self.cycle_number} exceeds group's total cycles {self.group.total_cycles}.")
        if self.amount <= Decimal('0'):
            raise ValidationError("Payout amount must be a positive number.")
        if self.status == self.STATUS_PAID and not self.actual_date:
            raise ValidationError("Paid payout must have actual_date set.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
