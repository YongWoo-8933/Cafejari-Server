from django.urls import path, include

from rest_framework import routers

from cafe_log.views import CafeLogViewSet

router = routers.DefaultRouter()
router.register('', CafeLogViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
