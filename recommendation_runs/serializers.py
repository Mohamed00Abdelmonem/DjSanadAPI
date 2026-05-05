from rest_framework import serializers


class RecommendationContextSerializer(serializers.Serializer):
    TIME_OF_DAY_CHOICES = ("morning", "afternoon", "evening", "night")
    USER_MOOD_CHOICES = ("calm", "anxious", "stressed", "happy")

    time_of_day = serializers.ChoiceField(choices=TIME_OF_DAY_CHOICES, required=False)
    user_mood = serializers.ChoiceField(choices=USER_MOOD_CHOICES, required=False)
    limit = serializers.IntegerField(required=False, min_value=1)

    def validate(self, attrs):
        if "limit" not in attrs:
            attrs["limit"] = 10
        return attrs


class RecommendationRequestSerializer(serializers.Serializer):
    context = RecommendationContextSerializer(required=False)

    def validate(self, data):
        if "context" not in data or data.get("context") is None:
            data["context"] = {}
        return data
