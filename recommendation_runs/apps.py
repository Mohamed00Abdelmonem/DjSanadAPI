from django.apps import AppConfig


class RecommendationRunsConfig(AppConfig):
    default_auto_field = 'django_mongodb_backend.fields.ObjectIdAutoField'
    name = 'recommendation_runs'
