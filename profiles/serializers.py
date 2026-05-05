from rest_framework import serializers

from .models import Profile


class AssessmentAnswersSerializer(serializers.Serializer):
    q1_social_interaction = serializers.IntegerField(min_value=0, max_value=3)
    q2_eye_contact = serializers.IntegerField(min_value=0, max_value=3)
    q3_conversation = serializers.IntegerField(min_value=0, max_value=3)
    q4_understanding_emotions = serializers.CharField(allow_blank=False, trim_whitespace=True)
    q5_auditory = serializers.IntegerField(min_value=0, max_value=3)
    q6_visual = serializers.IntegerField(min_value=0, max_value=3)
    q7_tactile = serializers.IntegerField(min_value=0, max_value=3)
    q8_sensory_overload = serializers.CharField(allow_blank=False, trim_whitespace=True)
    q9_routine = serializers.IntegerField(min_value=0, max_value=3)
    q10_support_needed = serializers.CharField(allow_blank=False, trim_whitespace=True)

    def _validate_non_empty(self, value, field_name):
        if not isinstance(value, str) or not value.strip():
            raise serializers.ValidationError(f"{field_name} must be a non-empty string.")
        return value

    def validate_q4_understanding_emotions(self, value):
        return self._validate_non_empty(value, "q4_understanding_emotions")

    def validate_q8_sensory_overload(self, value):
        return self._validate_non_empty(value, "q8_sensory_overload")

    def validate_q10_support_needed(self, value):
        return self._validate_non_empty(value, "q10_support_needed")


class AssessmentRequestSerializer(serializers.Serializer):
    language = serializers.ChoiceField(choices=("ar", "en"))
    answers = AssessmentAnswersSerializer()


class ProfileResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = (
            "profile_id",
            "language",
            "version",
            "summary",
            "social",
            "sensory",
            "support",
            "raw_data",
            "metadata",
            "created_at",
            "updated_at",
        )
