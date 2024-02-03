
from django.urls import path, include
from rest_framework import routers
from notification.views import PushNotificationViewSet, PopUpNotificationViewSet

router = routers.DefaultRouter()
router.register('pop_up', PopUpNotificationViewSet)
router.register('', PushNotificationViewSet)

urlpatterns = [
    path('', include(router.urls))
]