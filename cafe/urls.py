
from django.urls import path, include
from rest_framework import routers
from cafe.views import CafeViewSet, OccupancyRateUpdateLogViewSet, LocationViewSet, CATIViewSet

router = routers.DefaultRouter()
router.register('location', LocationViewSet)
router.register('', CafeViewSet)
router.register('occupancy_update_log', OccupancyRateUpdateLogViewSet)
router.register('cati', CATIViewSet)

urlpatterns = [
    path('', include(router.urls))
]