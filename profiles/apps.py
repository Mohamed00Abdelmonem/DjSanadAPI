from django.apps import AppConfig


class ProfilesConfig(AppConfig):
    default_auto_field = 'django_mongodb_backend.fields.ObjectIdAutoField'
    name = 'profiles'
