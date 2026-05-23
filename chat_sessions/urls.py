from django.urls import path
from .views import ChatSessionView, ChatMessageView

urlpatterns = [
    path("sessions/", ChatSessionView.as_view(), name="chat-session"),
    path("messages/", ChatMessageView.as_view(), name="chat-message"),
]
