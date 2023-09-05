
from django.urls import path, include
from rest_framework import routers
from cafe.views import CafeViewSet, OccupancyRateUpdateLogViewSet, LocationViewSet

router = routers.DefaultRouter()
router.register('location', LocationViewSet)
router.register('', CafeViewSet)
router.register('occupancy_update_log', OccupancyRateUpdateLogViewSet)

urlpatterns = [
    path('', include(router.urls))
]