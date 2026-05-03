from django.db import models
import django_mongodb_backend
from users.models import User
from profiles.models import Profile
# Create your models here.




class AssessmentRun(models.Model):
    id = django_mongodb_backend.fields.ObjectIdAutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)

    answers = models.JSONField()
    result_summary = models.JSONField()

    created_at = models.DateTimeField(auto_now_add=True)




    