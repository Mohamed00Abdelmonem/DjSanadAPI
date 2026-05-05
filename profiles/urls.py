from django.urls import path

from .views import AssessmentCreateView

app_name = "profiles"

urlpatterns = [
    path("", AssessmentCreateView.as_view(), name="assessment"),
]
