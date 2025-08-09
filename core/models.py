from django.db import models
from django.contrib.auth.models import AbstractUser

# User model
class User(AbstractUser):
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20, unique=True)
    national_id = models.CharField(max_length=100, blank=True, null=True)
    class Role(models.TextChoices):
        SYSTEM_ADMIN = 'system_admin', 'System Admin'
        GROUP_ADMIN = 'group_admin', 'Group Admin'
        MEMBER = 'member', 'Member'
    
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.MEMBER)

    REQUIRED_FIELDS = ['email', 'phone_number']
    USERNAME_FIELD = 'username' 

    def save(self, *args, **kwargs):
        if self.email:
            self.email = self.email.lower()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.username} ({self.role})"
        
