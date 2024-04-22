from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    phone_number = models.CharField(max_length=15, unique=True)
    auth_code = models.CharField(max_length=4, blank=True, null=True)
    invite_code = models.CharField(max_length=6, blank=True, null=True)
    activated_invite_code = models.BooleanField(default=False)
    username = models.CharField(max_length=150, unique=True, blank=True, null=True)

    def __str__(self):
        return self.phone_number

class InvitedUser(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    invited_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='invited_by')
