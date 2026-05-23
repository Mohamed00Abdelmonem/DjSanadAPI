import logging

from django.db import IntegrityError, transaction
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Profile
from .serializers import AssessmentRequestSerializer, ProfileResponseSerializer
from .services import ExternalAPIConfigError, ExternalAPIError, call_assessment_service

logger = logging.getLogger(__name__)


class AssessmentCreateView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = AssessmentRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {
                    "status": "error",
                    "message": f"Validation error: {serializer.errors}",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            profile_data = call_assessment_service(serializer.validated_data)
        except ExternalAPIConfigError as exc:
            logger.error("Assessment external API configuration error: %s", exc)
            return Response(
                {
                    "status": "error",
                    "message": str(exc),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        except ExternalAPIError as exc:
            logger.warning("Assessment external API failure: %s", exc)
            return Response(
                {
                    "status": "error",
                    "message": str(exc),
                },
                status=status.HTTP_502_BAD_GATEWAY,
            )
        except Exception:
            logger.exception("Unexpected error while calling external assessment API.")
            return Response(
                {
                    "status": "error",
                    "message": "Unexpected server error.",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        try:
            with transaction.atomic():
                existing_profile = Profile.objects.filter(user=request.user).first()
                if existing_profile:
                    existing_profile.delete()
                profile = Profile.objects.create(user=request.user, **profile_data)
        except IntegrityError:
            return Response(
                {
                    "status": "error",
                    "message": "Profile already exists.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception:
            logger.exception("Failed to save profile.")
            return Response(
                {
                    "status": "error",
                    "message": "Unexpected server error.",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(
            {
                "status": "success",
                "message": "Profile created successfully",
                "data": {
                    "profile_id": profile.profile_id,
                    "profile": ProfileResponseSerializer(profile).data,
                },
            },
            status=status.HTTP_201_CREATED,
        )
