from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from decimal import Decimal
from django.utils import timezone
from .group import EqubGroup, GroupMember
from .contribution import Contribution, PayoutSchedule

class Penalty(models.Model):
    TYPE_FIXED = "fixed"
    TYPE_PERCENT = "percent"
    TYPE_CHOICES = [
        (TYPE_FIXED, "Fixed amount"),
        (TYPE_PERCENT, "Percentage of expected amount"),
    ]

    STATUS_PENDING = "pending"
    STATUS_APPLIED = "applied"
    STATUS_REVERSED = "reversed"
    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_APPLIED, "Applied"),
        (STATUS_REVERSED, "Reversed"),
    ]

    group = models.ForeignKey(
        EqubGroup,
        on_delete=models.CASCADE,
        related_name="penalties"
    )
    member = models.ForeignKey(
        GroupMember,
        on_delete=models.CASCADE,
        related_name="penalties"
    )
    contribution = models.ForeignKey(
        Contribution,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="penalties"
    )
    payout_schedule = models.ForeignKey(
        PayoutSchedule,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="penalties"
    )

    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    value = models.DecimalField(max_digits=10, decimal_places=2)
    computed_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Final penalty amount when applied (stored for audit)."
    )
    reason = models.CharField(max_length=255, help_text="Short reason/code")
    notes = models.TextField(null=True, blank=True)
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING
    )
    applied_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="applied_penalties",
        help_text="User/system actor who applied/reversed the penalty"
    )
    applied_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["group", "member"]),
            models.Index(fields=["status"]),
        ]
        ordering = ["-created_at"]

    def __str__(self):
        return f"Penalty({self.group.id}, {self.member.id}, {self.type} {self.value})"

    def clean(self):
        # Either contribution or payout_schedule should be set, but not both
        if self.contribution and self.payout_schedule:
            raise ValidationError("Penalty cannot be linked to both a contribution and a payout_schedule simultaneously.")
        if not self.contribution and not self.payout_schedule:
            raise ValidationError("Penalty must be linked to either a contribution or a payout_schedule.")

        # Ensure penalty's group matches the group of contribution/payout_schedule if set
        if self.contribution and self.group != self.contribution.group:
            raise ValidationError("Penalty group must match the contribution's group.")
        if self.payout_schedule and self.group != self.payout_schedule.group:
            raise ValidationError("Penalty group must match the payout schedule's group.")

        # Ensure member belongs to the group
        if self.member.group != self.group:
            raise ValidationError("Penalty member must belong to the penalty's group.")

        # Value must be positive decimal
        if self.value <= Decimal('0'):
            raise ValidationError("Penalty value must be positive.")

    def compute_amount(self, expected_amount: Decimal | float):
        expected = Decimal(expected_amount)
        if self.type == self.TYPE_FIXED:
            return Decimal(self.value).quantize(Decimal("0.01"))
        elif self.type == self.TYPE_PERCENT:
            return (expected * Decimal(self.value) / Decimal("100")).quantize(Decimal("0.01"))
        else:
            raise ValueError("Unknown penalty type")

    def apply(self, expected_amount: Decimal | float, actor=None, when=None):
        if self.status == self.STATUS_APPLIED:
            return self
        self.computed_amount = self.compute_amount(expected_amount)
        self.status = self.STATUS_APPLIED
        if actor:
            self.applied_by = actor
        self.applied_at = when or timezone.now()
        self.save(update_fields=["computed_amount", "status", "applied_by", "applied_at", "updated_at"])
        return self

    def reverse(self, actor=None, when=None):
        if self.status == self.STATUS_REVERSED:
            return self
        self.status = self.STATUS_REVERSED
        if actor:
            self.applied_by = actor
        self.applied_at = when or timezone.now()
        self.save(update_fields=["status", "applied_by", "applied_at", "updated_at"])
        return self
