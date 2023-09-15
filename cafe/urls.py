
from django.urls import path, include
from rest_framework import routers
from cafe.views import CafeViewSet, OccupancyRateUpdateLogViewSet, LocationViewSet, CATIViewSet

router = routers.DefaultRouter()
router.register('occupancy_update_log', OccupancyRateUpdateLogViewSet)
router.register('cati', CATIViewSet)
router.register('location', LocationViewSet)
router.register('', CafeViewSet)

urlpatterns = [
    path('', include(router.urls))
]