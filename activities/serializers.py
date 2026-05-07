from rest_framework import serializers

from .models import Activity, ActivityCategory


class ActivitySerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)
    average_rating = serializers.FloatField(read_only=True)
    total_ratings = serializers.IntegerField(read_only=True)

    class Meta:
        model = Activity
        fields = (
            'id',
            'name',
            'description',
            'category',
            'time_takes',
            'emoji',
            'steps',
            'average_rating',
            'total_ratings',
        )


class ActivityCreateUpdateSerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)
    steps = serializers.ListField(
        child=serializers.CharField(allow_blank=False, trim_whitespace=True),
        allow_empty=False,
    )
    emoji = serializers.CharField(min_length=1, max_length=8)
    time_takes = serializers.IntegerField(min_value=1)

    class Meta:
        model = Activity
        fields = (
            'id',
            'name',
            'description',
            'category',
            'time_takes',
            'emoji',
            'steps',
        )
        read_only_fields = ('id',)

    def validate_steps(self, value):
        if not isinstance(value, list) or not value:
            raise serializers.ValidationError('Steps must be a non-empty array of strings.')

        cleaned = []
        for step in value:
            if not isinstance(step, str):
                raise serializers.ValidationError('Each step must be a string.')
            if not step.strip():
                raise serializers.ValidationError('Steps must not be empty strings.')
            cleaned.append(step.strip())

        return cleaned

    def validate_category(self, value):
        if value not in ActivityCategory.values:
            raise serializers.ValidationError('Invalid category.')
        return value


class ActivityRatingSerializer(serializers.Serializer):
    rate = serializers.IntegerField(min_value=1, max_value=5)
