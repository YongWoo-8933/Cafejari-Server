
from django.urls import path, include
from rest_framework import routers
from leaderboard.views import TotalSharingRankerViewSet, WeekSharingRankerViewSet, MonthSharingRankerViewSet, \
    MonthlyHotCafeLogViewSet

router = routers.DefaultRouter()
router.register('total_sharing_ranker', TotalSharingRankerViewSet)
router.register('month_sharing_ranker', MonthSharingRankerViewSet)
router.register('week_sharing_ranker', WeekSharingRankerViewSet)
router.register('monthly_hot_cafe_log', MonthlyHotCafeLogViewSet)

urlpatterns = [
    path('', include(router.urls))
]
