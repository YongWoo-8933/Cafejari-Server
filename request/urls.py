
from django.urls import path, include
from rest_framework import routers

from request.views import CafeAdditionRequestViewSet

router = routers.DefaultRouter()
router.register('cafe_addition', CafeAdditionRequestViewSet)
# router.register('withdrawal', WithdrawalRequestViewSet)
# router.register('user_migration', UserMigrationRequestViewSet)

urlpatterns = [
    path('', include(router.urls))
]