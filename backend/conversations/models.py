from django.conf import settings
from django.db import models


class ChatThread(models.Model):
  user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="chat_threads")
  stock = models.ForeignKey("market.Stock", on_delete=models.SET_NULL, null=True, blank=True, related_name="chat_threads")
  title = models.CharField(max_length=255)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

  class Meta:
    ordering = ["-updated_at"]

  def __str__(self) -> str:
    return self.title


class ChatMessage(models.Model):
  class Role(models.TextChoices):
    USER = "user", "User"
    ASSISTANT = "assistant", "Assistant"
    SYSTEM = "system", "System"

  thread = models.ForeignKey(ChatThread, on_delete=models.CASCADE, related_name="messages")
  role = models.CharField(max_length=20, choices=Role.choices)
  content = models.TextField()
  metadata = models.JSONField(default=dict, blank=True)
  created_at = models.DateTimeField(auto_now_add=True)

  class Meta:
    ordering = ["created_at"]


class DebateSession(models.Model):
  class Status(models.TextChoices):
    PENDING = "pending", "Pending"
    RUNNING = "running", "Running"
    COMPLETED = "completed", "Completed"
    FAILED = "failed", "Failed"

  user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="debate_sessions")
  stock = models.ForeignKey("market.Stock", on_delete=models.SET_NULL, null=True, blank=True, related_name="debate_sessions")
  topic = models.CharField(max_length=255)
  status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
  summary = models.TextField(blank=True)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

  class Meta:
    ordering = ["-created_at"]

  def __str__(self) -> str:
    return self.topic


class DebateMessage(models.Model):
  session = models.ForeignKey(DebateSession, on_delete=models.CASCADE, related_name="messages")
  agent_name = models.CharField(max_length=100)
  agent_role = models.CharField(max_length=50)
  round_number = models.PositiveIntegerField(default=1)
  content = models.TextField()
  created_at = models.DateTimeField(auto_now_add=True)

  class Meta:
    ordering = ["round_number", "created_at"]
