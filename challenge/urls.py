
from django.urls import path, include
from rest_framework import routers

from challenge.views import ChallengeViewSet, ChallengerViewSet

router = routers.DefaultRouter()
router.register('', ChallengeViewSet)
router.register('challenger', ChallengerViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
