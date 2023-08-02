
from django.urls import path, include
from rest_framework import routers
from cafe.views import CafeViewSet, OccupancyRateUpdateLogViewSet

router = routers.DefaultRouter()
router.register('', CafeViewSet)
router.register('occupancy_update_log', OccupancyRateUpdateLogViewSet)

urlpatterns = [
    path('', include(router.urls))
]