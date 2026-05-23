from django.db import models
import django_mongodb_backend
from users.models import User
# Create your models here.

class Profile(models.Model):
    id = django_mongodb_backend.fields.ObjectIdAutoField(primary_key=True)
    profile_id = models.CharField(max_length=100, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    language = models.CharField(max_length=10)

    # 🔥 Store full nested structure
    social_analysis = models.JSONField(default=dict)
    sensory_analysis = models.JSONField(default=dict)
    support_analysis = models.JSONField(default=dict)

    assessment_completed = models.BooleanField(default=True)

    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    def __str__(self):
        return self.profile_id
