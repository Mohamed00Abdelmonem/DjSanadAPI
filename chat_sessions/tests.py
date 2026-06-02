from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from .serializers import ChatMessageRequestSerializer


class ChatMessageRequestSerializerTests(TestCase):
    def test_accepts_message_only_payload(self):
        serializer = ChatMessageRequestSerializer(
            data={
                "session_id": "session_123",
                "message": "Hello",
            }
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_accepts_uploaded_image_in_image_data(self):
        image_file = SimpleUploadedFile(
            "photo.jpg",
            b"fake-image-content",
            content_type="image/jpeg",
        )
        serializer = ChatMessageRequestSerializer(
            data={
                "session_id": "session_123",
                "message": "",
                "image_data": image_file,
            }
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(serializer.validated_data["image_data"].name, "photo.jpg")

    def test_rejects_payload_without_message_image_or_audio(self):
        serializer = ChatMessageRequestSerializer(
            data={
                "session_id": "session_123",
                "message": "   ",
            }
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("non_field_errors", serializer.errors)
