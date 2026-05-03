from django.db import models
import django_mongodb_backend
from users.models import User
# Create your models here.

class Profile(models.Model):
    id = django_mongodb_backend.fields.ObjectIdAutoField(primary_key=True)
    profile_id = models.CharField(max_length=100, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    language = models.CharField(max_length=10)
    version = models.CharField(max_length=10, default="1.0")

    # 🔥 Store full nested structure
    summary = models.JSONField()
    social = models.JSONField()
    sensory = models.JSONField()
    support = models.JSONField()
    raw_data = models.JSONField()
    metadata = models.JSONField()

    assessment_completed = models.BooleanField(default=True)

    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    def __str__(self):
        return self.profile_id
