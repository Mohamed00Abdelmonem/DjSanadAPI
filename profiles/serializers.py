from rest_framework import serializers

from .models import Profile


class AssessmentAnswersSerializer(serializers.Serializer):
    q1_social_interaction = serializers.IntegerField(min_value=0, max_value=3)
    q2_eye_contact = serializers.IntegerField(min_value=0, max_value=3)
    q3_conversation = serializers.IntegerField(min_value=0, max_value=3)
    q5_auditory = serializers.IntegerField(min_value=0, max_value=3)
    q6_visual = serializers.IntegerField(min_value=0, max_value=3)
    q7_tactile = serializers.IntegerField(min_value=0, max_value=3)


class AssessmentRequestSerializer(serializers.Serializer):
    language = serializers.ChoiceField(choices=("ar", "en"))
    answers = AssessmentAnswersSerializer()


class ProfileResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = (
            "language",
            "social_analysis",
            "sensory_analysis",
            "support_analysis",
        )
