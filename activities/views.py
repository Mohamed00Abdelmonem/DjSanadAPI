from django.db import transaction
from django.db.models import Avg, Count, Value
from django.db.models.functions import Coalesce
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiResponse,
    OpenApiTypes,
    extend_schema,
    extend_schema_view,
)

from .models import Activity, ActivityCategory, ActivityRating
from .permissions import IsAdminOrAuthenticatedReadOnly
from .serializers import ActivityCreateUpdateSerializer, ActivityRatingSerializer, ActivitySerializer


AUTH_HEADER_PARAM = OpenApiParameter(
    name='Authorization',
    type=OpenApiTypes.STR,
    location=OpenApiParameter.HEADER,
    description='Bearer <access_token>',
    required=True,
)


@extend_schema_view(
    list=extend_schema(
        summary='List activities',
        description='List all activities (soft-deleted activities are excluded).',
        parameters=[
            AUTH_HEADER_PARAM,
            OpenApiParameter(
                name='category',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Filter by category.',
                required=False,
            ),
        ],
        responses={200: ActivitySerializer(many=True)},
        examples=[
            OpenApiExample(
                'List activities',
                value=[
                    {
                        'id': '507f1f77bcf86cd799439012',
                        'name': 'Deep Breathing',
                        'description': 'Helps reduce stress',
                        'category': 'breathing',
                        'time_takes': 5,
                        'emoji': ':)',
                        'steps': [
                            'Sit comfortably',
                            'Close your eyes',
                            'Take a deep breath',
                        ],
                        'average_rating': 4.8,
                        'total_ratings': 120,
                    }
                ],
                response_only=True,
            ),
        ],
    ),
    retrieve=extend_schema(
        summary='Get activity detail',
        description='Retrieve a single activity by id.',
        parameters=[AUTH_HEADER_PARAM],
        responses={200: ActivitySerializer},
    ),
    create=extend_schema(
        summary='Create activity (admin only)',
        parameters=[AUTH_HEADER_PARAM],
        request=ActivityCreateUpdateSerializer,
        responses={201: ActivitySerializer},
        examples=[
            OpenApiExample(
                'Create activity',
                value={
                    'name': 'Deep Breathing',
                    'description': 'Helps reduce stress',
                    'category': 'breathing',
                    'time_takes': 5,
                    'emoji': ':)',
                    'steps': [
                        'Sit comfortably',
                        'Close your eyes',
                        'Take a deep breath',
                    ],
                },
                request_only=True,
            ),
        ],
    ),
    partial_update=extend_schema(
        summary='Update activity (admin only)',
        parameters=[AUTH_HEADER_PARAM],
        request=ActivityCreateUpdateSerializer,
        responses={200: ActivitySerializer},
    ),
    update=extend_schema(
        summary='Update activity (admin only)',
        parameters=[AUTH_HEADER_PARAM],
        request=ActivityCreateUpdateSerializer,
        responses={200: ActivitySerializer},
    ),
    destroy=extend_schema(
        summary='Delete activity (admin only)',
        description='Soft delete an activity. Deleted activities are hidden from queries.',
        parameters=[AUTH_HEADER_PARAM],
        responses={204: OpenApiResponse(description='No content')},
    ),
)
class ActivityViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAdminOrAuthenticatedReadOnly,)
    filter_backends = []
    pagination_class = None

    @staticmethod
    def _normalize_category_param(category):
        if category is None:
            return None
        return category.strip().strip('"').strip("'")

    def get_queryset(self):
        queryset = Activity.objects.all()

        if self.action == 'list':
            category = self._normalize_category_param(
                self.request.query_params.get('category')
            )
            if category:
                if category not in ActivityCategory.values:
                    raise ValidationError({'category': 'Invalid category.'})
                queryset = queryset.filter(category=category)

        return queryset.annotate(
            average_rating=Coalesce(Avg('ratings__rate'), Value(0.0)),
            total_ratings=Coalesce(Count('ratings'), Value(0)),
        )

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return ActivityCreateUpdateSerializer
        if self.action == 'rate':
            return ActivityRatingSerializer
        return ActivitySerializer

    def get_permissions(self):
        if self.action == 'rate':
            return [IsAuthenticated()]
        return super().get_permissions()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_deleted = True
        instance.updated_at = timezone.now()
        instance.save(update_fields=['is_deleted', 'updated_at'])
        return Response(status=status.HTTP_204_NO_CONTENT)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        activity = self.get_queryset().filter(id=serializer.instance.id).first()
        response_serializer = ActivitySerializer(activity, context=self.get_serializer_context())
        headers = self.get_success_headers(response_serializer.data)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        activity = self.get_queryset().filter(id=instance.id).first()
        response_serializer = ActivitySerializer(activity, context=self.get_serializer_context())
        return Response(response_serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary='Rate activity',
        description='Create or update the authenticated user\'s rating for this activity.',
        parameters=[AUTH_HEADER_PARAM],
        request=ActivityRatingSerializer,
        responses={200: ActivitySerializer},
        examples=[
            OpenApiExample(
                'Rate activity',
                value={'rate': 5},
                request_only=True,
            ),
        ],
    )
    @action(detail=True, methods=['post'], url_path='rate')
    def rate(self, request, *args, **kwargs):
        activity = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        rate_value = serializer.validated_data['rate']

        with transaction.atomic():
            ActivityRating.objects.update_or_create(
                user=request.user,
                activity=activity,
                defaults={'rate': rate_value},
            )
            Activity.objects.filter(id=activity.id).update(updated_at=timezone.now())

        refreshed = self.get_queryset().filter(id=activity.id).first()
        response_serializer = ActivitySerializer(refreshed, context=self.get_serializer_context())
        return Response(response_serializer.data, status=status.HTTP_200_OK)
