from rest_framework.routers import DefaultRouter

from .views import ActivityViewSet

app_name = 'activities'

router = DefaultRouter()
router.register(r'', ActivityViewSet, basename='activities')

urlpatterns = router.urls
