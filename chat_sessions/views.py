import logging
import uuid
from django.db import transaction
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from profiles.models import Profile
from chat_messages.models import ChatMessage
from .models import ChatSession
from .serializers import (
    ChatSessionCreateSerializer,
    ChatSessionResponseSerializer,
    ChatMessageRequestSerializer,
    ChatMessageResponseSerializer,
)
from .services import ExternalAPIConfigError, ExternalAPIError, call_chat_service

logger = logging.getLogger(__name__)


class ChatSessionView(APIView):
    """
    POST /api/chat/sessions/ - Create a new chat session.
    GET /api/chat/sessions/  - Retrieve all chat sessions for the authenticated user.
    """
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = ChatSessionCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {
                    "status": "error",
                    "message": f"Validation error: {serializer.errors}",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        session_type = serializer.validated_data["type"]

        try:
            profile = Profile.objects.get(user=request.user)
        except Profile.DoesNotExist:
            return Response(
                {
                    "status": "error",
                    "message": "User profile not found. Please complete the assessment first.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        # Auto-generate a unique session_id
        while True:
            session_id = f"session_{uuid.uuid4().hex[:12]}"
            if not ChatSession.objects.filter(session_id=session_id).exists():
                break

        try:
            session = ChatSession.objects.create(
                session_id=session_id,
                user=request.user,
                profile=profile,
                type=session_type,
                language=profile.language,
            )
        except Exception:
            logger.exception("Failed to create chat session.")
            return Response(
                {
                    "status": "error",
                    "message": "Failed to create chat session.",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(
            {
                "status": "success",
                "message": "Chat session created successfully",
                "data": ChatSessionResponseSerializer(session).data,
            },
            status=status.HTTP_201_CREATED,
        )

    def get(self, request):
        sessions = ChatSession.objects.filter(user=request.user).order_by("-created_at")
        serializer = ChatSessionResponseSerializer(sessions, many=True)
        return Response(
            {
                "status": "success",
                "data": {
                    "sessions": serializer.data,
                },
            },
            status=status.HTTP_200_OK,
        )


class ChatMessageView(APIView):
    """
    POST /api/chat/messages/ - Send a message (text, image, or audio) in an existing chat session.
    GET /api/chat/messages/  - Retrieve all messages in a session.
    """
    permission_classes = (IsAuthenticated,)
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    def post(self, request):
        serializer = ChatMessageRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {
                    "status": "error",
                    "message": f"Validation error: {serializer.errors}",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        session_id = serializer.validated_data["session_id"]
        message = serializer.validated_data["message"]
        image_file = serializer.validated_data.get("image_data")
        audio_file = serializer.validated_data.get("audio")

        try:
            session = ChatSession.objects.get(session_id=session_id, user=request.user)
        except ChatSession.DoesNotExist:
            return Response(
                {
                    "status": "error",
                    "message": "Chat session not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            profile = Profile.objects.get(user=request.user)
        except Profile.DoesNotExist:
            return Response(
                {
                    "status": "error",
                    "message": "User profile not found. Please complete the assessment first.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            service_data = call_chat_service(
                session_id,
                profile.profile_id,
                message,
                image_file=image_file,
                audio_file=audio_file,
            )
        except ExternalAPIConfigError as exc:
            logger.error("Chat external API configuration error: %s", exc)
            return Response(
                {
                    "status": "error",
                    "message": str(exc),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        except ExternalAPIError as exc:
            logger.warning("Chat external API failure: %s", exc)
            return Response(
                {
                    "status": "error",
                    "message": str(exc),
                },
                status=status.HTTP_502_BAD_GATEWAY,
            )
        except Exception:
            logger.exception("Unexpected error while calling external chat API.")
            return Response(
                {
                    "status": "error",
                    "message": "Unexpected server error.",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # Build database content and input type
        input_type = "text"
        db_content = {"text": message}
        if image_file:
            input_type = "image"
            db_content["image_name"] = image_file.name
        elif audio_file:
            input_type = "audio"
            db_content["audio_name"] = audio_file.name

        try:
            with transaction.atomic():
                ChatMessage.objects.create(
                    session=session,
                    user=request.user,
                    role="user",
                    input_type=input_type,
                    content=db_content
                )
                ChatMessage.objects.create(
                    session=session,
                    user=request.user,
                    role="assistant",
                    input_type="text",
                    content={"text": service_data["ai_response"]},
                    route=service_data["response_type"]
                )
        except Exception:
            logger.exception("Failed to save chat messages in database.")
            return Response(
                {
                    "status": "error",
                    "message": "Failed to save conversation message history.",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(
            {
                "status": service_data["status"],
                "ai_response": service_data["ai_response"],
            },
            status=status.HTTP_201_CREATED,
        )

    def get(self, request):
        session_id = request.query_params.get("session_id")
        if not session_id:
            return Response(
                {
                    "status": "error",
                    "message": "session_id query parameter is required.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            session = ChatSession.objects.get(session_id=session_id, user=request.user)
        except ChatSession.DoesNotExist:
            return Response(
                {
                    "status": "error",
                    "message": "Chat session not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        messages = ChatMessage.objects.filter(session=session).order_by("created_at")
        serializer = ChatMessageResponseSerializer(messages, many=True)

        return Response(
            {
                "status": "success",
                "data": {
                    "session_id": session_id,
                    "messages": serializer.data,
                },
            },
            status=status.HTTP_200_OK,
        )
