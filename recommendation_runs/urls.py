from django.urls import path

from .views import RecommendationCreateView

app_name = "recommendation_runs"

urlpatterns = [
    path("", RecommendationCreateView.as_view(), name="recommendations"),
]
