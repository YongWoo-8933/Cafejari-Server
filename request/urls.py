
from django.urls import path, include
from rest_framework import routers

from request.views import CafeAdditionRequestViewSet, WithdrawalRequestViewSet, UserMigrationRequestViewSet, \
    CafeInformationSuggestionViewSet

router = routers.DefaultRouter()
router.register('cafe_addition', CafeAdditionRequestViewSet)
router.register('cafe_information_suggestion', CafeInformationSuggestionViewSet)
router.register('withdrawal', WithdrawalRequestViewSet)
router.register('user_migration', UserMigrationRequestViewSet)

urlpatterns = [
    path('', include(router.urls))
]