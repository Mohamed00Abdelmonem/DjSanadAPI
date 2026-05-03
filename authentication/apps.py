from django.apps import AppConfig
import django_mongodb_backend


class AuthenticationConfig(AppConfig):
    default_auto_field = 'django_mongodb_backend.fields.ObjectIdAutoField'
    name = 'authentication'
