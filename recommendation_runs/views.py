import logging

from django.db import transaction
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from profiles.models import Profile

from .models import RecommendationRun
from .serializers import RecommendationRequestSerializer
from .services import ExternalAPIConfigError, ExternalAPIError, call_recommendations_service

logger = logging.getLogger(__name__)


def _serialize_profile(profile: Profile):
	def _to_iso(value):
		return value.isoformat() if value else None

	return {
		"profile_id": profile.profile_id,
		"language": profile.language,
		"social_analysis": profile.social_analysis,
		"sensory_analysis": profile.sensory_analysis,
		"support_analysis": profile.support_analysis,
		"assessment_completed": profile.assessment_completed,
		"created_at": _to_iso(profile.created_at),
		"updated_at": _to_iso(profile.updated_at),
	}


class RecommendationCreateView(APIView):
	"""
	POST /api/recommendations/

	Generate recommendations for the authenticated user.
	Requires an existing profile for the user.

	Authentication:
	Authorization: Bearer <access_token>

	Request body:
	{
		"context": {
			"time_of_day": "morning",
			"user_mood": "calm",
			"limit": 8
		}
	}

	Response:
	{
		"status": "success",
		"message": "...",
		"data": {
			"timestamp": "...",
			"context_used": { ... },
			"recommendations": [ ... ],
			"summary": { ... },
			"metadata": { ... }
		}
	}
	"""
	permission_classes = (IsAuthenticated,)

	def post(self, request):
		serializer = RecommendationRequestSerializer(data=request.data)
		if not serializer.is_valid():
			return Response(
				{
					"status": "error",
					"message": f"Validation error: {serializer.errors}",
				},
				status=status.HTTP_400_BAD_REQUEST,
			)

		context = serializer.validated_data.get("context") or {}

		try:
			profile = Profile.objects.get(user=request.user)
		except Profile.DoesNotExist:
			return Response(
				{
					"status": "error",
					"message": "Profile not found.",
				},
				status=status.HTTP_404_NOT_FOUND,
			)

		user_profile = _serialize_profile(profile)

		try:
			service_data = call_recommendations_service(user_profile, context)
		except ExternalAPIConfigError as exc:
			logger.error("Recommendations API configuration error: %s", exc)
			return Response(
				{
					"status": "error",
					"message": str(exc),
				},
				status=status.HTTP_500_INTERNAL_SERVER_ERROR,
			)
		except ExternalAPIError as exc:
			logger.warning("Recommendations API failure: %s", exc)
			return Response(
				{
					"status": "error",
					"message": str(exc),
				},
				status=status.HTTP_502_BAD_GATEWAY,
			)
		except Exception:
			logger.exception("Unexpected error while calling recommendations API.")
			return Response(
				{
					"status": "error",
					"message": "Unexpected server error.",
				},
				status=status.HTTP_500_INTERNAL_SERVER_ERROR,
			)

		context_used = service_data.get("context_used") or context

		try:
			with transaction.atomic():
				RecommendationRun.objects.create(
					user=request.user,
					context=context_used,
					recommendations=service_data["recommendations"],
					summary=service_data["summary"],
				)
		except Exception:
			logger.exception("Failed to save recommendation run.")
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
				"message": service_data.get("message", "Recommendations generated successfully"),
				"data": {
					# "timestamp": service_data["timestamp"],
					"context_used": context_used,
					"recommendations": service_data["recommendations"],
					"summary": service_data["summary"],
					"metadata": service_data["metadata"],
				},
			},
			status=status.HTTP_201_CREATED,
		)
