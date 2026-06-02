from rest_framework import serializers
from chat_messages.models import ChatMessage


class ChatSessionCreateSerializer(serializers.Serializer):
    type = serializers.ChoiceField(choices=("ai_agent", "sanad_chat"), default="ai_agent")


class ChatSessionResponseSerializer(serializers.ModelSerializer):
    class Meta:
        from .models import ChatSession
        model = ChatSession
        fields = (
            "session_id",
            "type",
            "language",
            "created_at",
        )


class ChatMessageRequestSerializer(serializers.Serializer):
    session_id = serializers.CharField(max_length=100)
    message = serializers.CharField(required=False, allow_blank=True, default="")
    image_data = serializers.FileField(required=False, allow_empty_file=False)
    audio = serializers.FileField(required=False, allow_empty_file=False)

    def validate(self, attrs):
        message = attrs.get("message", "").strip()
        image_file = attrs.get("image_data")
        audio_file = attrs.get("audio")

        if not any((message, image_file, audio_file)):
            raise serializers.ValidationError(
                "Provide at least one of message, image_data, or audio."
            )

        attrs["message"] = message
        return attrs


class ChatMessageResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = (
            "role",
            "input_type",
            "content",
            "route",
            "created_at",
        )
