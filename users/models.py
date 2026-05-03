from django.db import models
import django_mongodb_backend

class User(models.Model):
    id = django_mongodb_backend.fields.ObjectIdAutoField(primary_key=True)
    user_id = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    password_hash = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user_id