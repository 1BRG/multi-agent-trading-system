from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from accounts.models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
  fieldsets = UserAdmin.fieldsets + (
      ("AI Stock Lab", {"fields": ("full_name", "role", "created_at", "updated_at")}),
  )
  readonly_fields = ("created_at", "updated_at")
  list_display = ("id", "username", "email", "role", "is_active", "is_staff")
  search_fields = ("username", "email", "full_name")
