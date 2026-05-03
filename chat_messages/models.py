from django.db import models
import django_mongodb_backend
from users.models import User
from chat_sessions.models import ChatSession
# Create your models here.


class ChatMessage(models.Model):
    id = django_mongodb_backend.fields.ObjectIdAutoField(primary_key=True)
    ROLES = [
        ("user", "User"),
        ("assistant", "Assistant"),
    ]

    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    role = models.CharField(max_length=10, choices=ROLES)
    input_type = models.CharField(max_length=20, default="text")

    content = models.JSONField()

    # For AI routing
    route = models.CharField(max_length=50, null=True, blank=True)
    analysis = models.JSONField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)