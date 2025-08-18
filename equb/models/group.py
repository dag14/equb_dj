import uuid
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from decimal import Decimal
from django.utils import timezone


class EqubGroup(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_STARTED = 'started'
    STATUS_COMPLETED = 'completed'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_STARTED, 'Started'),
        (STATUS_COMPLETED, 'Completed'),
    ]
    
    id = models.UUIDField(primary_key=True, default = uuid.uuid4, editable = False)
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    admin = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='owned_groups',
        null=True,  # allow temporary None
        blank=True
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING
    )
    contribution_amount = models.DecimalField(max_digits=10, decimal_places=2)
    total_cycles = models.PositiveIntegerField()
    current_cycle = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    ROTATION_RANDOM = 'random'
    ROTATION_SEQUENTIAL = 'sequential'
    ROTATION_CUSTOM = 'custom'

    ROTATION_CHOICES = [
        (ROTATION_RANDOM, 'Random'),
        (ROTATION_SEQUENTIAL, 'Sequential'),
        (ROTATION_CUSTOM, 'Custom'),
    ]

    rotation_rule = models.CharField(
        max_length=20,
        choices=ROTATION_CHOICES,
        default=ROTATION_RANDOM,
        help_text="Defines the payout rotation logic for the Equb group"
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Equb Groups"

    def __str__(self):
        return f"{self.name} ({self.status})"

    def clean(self):
        # if not self.admin:
        #     raise ValidationError("Group must have an admin.")
        if self.admin is None:
        # Skip raising error in development
            return
        if self.status == self.STATUS_STARTED and not self.started_at:
            raise ValidationError("Started groups must have a started_at datetime.")
        if self.status == self.STATUS_COMPLETED and not self.completed_at:
            raise ValidationError("Completed groups must have a completed_at datetime.")
        if self.status == self.STATUS_PENDING:
            if self.started_at or self.completed_at:
                raise ValidationError("Pending groups cannot have started_at or completed_at set.")
        if self.pk:
            member_count = self.memberships.filter(status=GroupMember.STATUS_ACTIVE).count()
            if self.total_cycles < member_count:
                raise ValidationError(f"Total cycles ({self.total_cycles}) cannot be less than the number of active members ({member_count}).")
            if self.contribution_amount <= Decimal('0'):
                raise ValidationError("Contribution amount must be a positive number.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
    def can_start(self):
        # Only pending groups with at least 2 active members can start
        active_members = self.memberships.filter(status=GroupMember.STATUS_ACTIVE).count()
        return self.status == self.STATUS_PENDING and active_members >= 2

    def can_complete(self):
        # Only started groups can be completed
        return self.status == self.STATUS_STARTED

    def start(self):
        if not self.can_start():
            raise ValidationError("Group cannot be started yet. Ensure it is pending and has enough active members.")
        self.status = self.STATUS_STARTED
        self.started_at = timezone.now()
        self.save()

    def complete(self):
        if not self.can_complete():
            raise ValidationError("Group cannot be completed yet. Only started groups can be completed.")
        self.status = self.STATUS_COMPLETED
        self.completed_at = timezone.now()
        self.save()


class GroupMember(models.Model):
    ROLE_ADMIN = 'group_admin'
    ROLE_MEMBER = 'member'

    ROLE_CHOICES = [
        (ROLE_ADMIN, 'Group Admin'),
        (ROLE_MEMBER, 'Member'),
    ]

    STATUS_ACTIVE = 'active'
    STATUS_LEFT = 'left'
    STATUS_REMOVED = 'removed'

    STATUS_CHOICES = [
        (STATUS_ACTIVE, 'Active'),
        (STATUS_LEFT, 'Left'),
        (STATUS_REMOVED, 'Removed'),
    ]
    id = models.UUIDField(primary_key=True, default = uuid.uuid4, editable = False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='group_memberships'
    )
    group = models.ForeignKey(
        EqubGroup,
        on_delete=models.CASCADE,
        related_name='memberships'
    )
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default=ROLE_MEMBER
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_ACTIVE
    )
    joined_at = models.DateTimeField(auto_now_add=True)
    has_won = models.BooleanField(default=False)


    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'group'], name='unique_user_group_membership')
        ]
        ordering = ['joined_at']

    def __str__(self):
        return f"{self.user.username} in {self.group.name} ({self.role})"
