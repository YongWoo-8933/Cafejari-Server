
from django.urls import path, include
from rest_framework import routers

from app_config.views import VersionViewSet

router = routers.DefaultRouter()
router.register('version', VersionViewSet)

urlpatterns = [
    path('', include(router.urls))
]