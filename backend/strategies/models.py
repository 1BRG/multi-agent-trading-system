from django.conf import settings
from django.db import models


class Strategy(models.Model):
  class Status(models.TextChoices):
    DRAFT = "draft", "Draft"
    APPROVED = "approved", "Approved"
    ARCHIVED = "archived", "Archived"

  class Source(models.TextChoices):
    MANUAL = "manual", "Manual"
    AI = "ai", "AI"

  owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="strategies")
  name = models.CharField(max_length=255)
  description = models.TextField(blank=True)
  config = models.JSONField(default=dict, blank=True)
  status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
  source = models.CharField(max_length=20, choices=Source.choices, default=Source.MANUAL)
  # Store the raw LLM response for audit/debugging when a strategy is created via AI
  raw_llm_response = models.TextField(blank=True)
  is_public = models.BooleanField(default=False)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

  class Meta:
    indexes = [
        models.Index(fields=["owner", "is_public"], name="strategy_owner_public_idx"),
    ]
    ordering = ["-created_at"]

  def __str__(self) -> str:
    return self.name
