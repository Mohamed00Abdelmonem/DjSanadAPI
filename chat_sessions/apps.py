from django.apps import AppConfig


class ChatSessionsConfig(AppConfig):
    default_auto_field = 'django_mongodb_backend.fields.ObjectIdAutoField'
    name = 'chat_sessions'
