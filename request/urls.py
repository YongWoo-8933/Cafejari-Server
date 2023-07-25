
from django.urls import path, include
from rest_framework import routers

from request.views import CafeAdditionRequestViewSet

router = routers.DefaultRouter()
router.register('cafe_addition', CafeAdditionRequestViewSet)

urlpatterns = [
    path('', include(router.urls))
]