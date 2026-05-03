from django.db import models
import django_mongodb_backend
from users.models import User
from profiles.models import Profile
# Create your models here.


class ChatSession(models.Model):
    id = django_mongodb_backend.fields.ObjectIdAutoField(primary_key=True)
    SESSION_TYPES = [
        ("ai_agent", "AI Agent"),
        ("sanad_chat", "Sanad Chat"),
    ]

    session_id = models.CharField(max_length=100, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)

    type = models.CharField(max_length=20, choices=SESSION_TYPES)
    language = models.CharField(max_length=10)

    context = models.JSONField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)