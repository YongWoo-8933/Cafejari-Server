
from django.urls import path, include
from rest_framework import routers
from notification.views import PushNotificationViewSet

router = routers.DefaultRouter()
router.register('', PushNotificationViewSet)

urlpatterns = [
    path('', include(router.urls))
]