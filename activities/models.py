from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
import django_mongodb_backend

from users.models import User


class ActivityCategory(models.TextChoices):
    BREATHING = 'breathing', 'Breathing'
    MEDITATION = 'meditation', 'Meditation'
    SLEEP = 'sleep', 'Sleep'
    RELAXATION = 'relaxation', 'Relaxation'
    FOCUS = 'focus', 'Focus'
    ANXIETY_RELIEF = 'anxiety_relief', 'Anxiety relief'


class ActivityQuerySet(models.QuerySet):
    def alive(self):
        return self.filter(is_deleted=False)

    def delete(self):
        return super().update(is_deleted=True)

    def hard_delete(self):
        return super().delete()


class ActivityManager(models.Manager.from_queryset(ActivityQuerySet)):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)


class Activity(models.Model):
    id = django_mongodb_backend.fields.ObjectIdAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=30, choices=ActivityCategory.choices)
    time_takes = models.IntegerField(validators=[MinValueValidator(1)])
    emoji = models.CharField(max_length=8)
    steps = models.JSONField(default=list)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = ActivityManager()
    all_objects = models.Manager()

    class Meta:
        indexes = [
            models.Index(fields=['category']),
            models.Index(fields=['is_deleted']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return self.name


class ActivityRating(models.Model):
    id = django_mongodb_backend.fields.ObjectIdAutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activity_ratings')
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, related_name='ratings')
    rate = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'activity'], name='unique_user_activity_rating'),
        ]
        indexes = [
            models.Index(fields=['activity', 'created_at']),
            models.Index(fields=['user', 'created_at']),
        ]

    def __str__(self):
        return f"{self.user_id}:{self.activity_id}:{self.rate}"
