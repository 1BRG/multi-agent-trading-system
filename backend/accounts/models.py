from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.functions import Lower


class User(AbstractUser):
  class Role(models.TextChoices):
    USER = "user", "User"
    ADMIN = "admin", "Admin"

  email = models.EmailField(unique=True)
  full_name = models.CharField(max_length=255, blank=True)
  role = models.CharField(max_length=50, choices=Role.choices, default=Role.USER)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

  class Meta:
    constraints = [
        models.UniqueConstraint(Lower("email"), name="accounts_user_email_ci_unique"),
        models.UniqueConstraint(Lower("username"), name="accounts_user_username_ci_unique"),
    ]

  def save(self, *args, **kwargs):
    self.email = self.email.strip().lower()
    self.username = self.username.strip()
    super().save(*args, **kwargs)
