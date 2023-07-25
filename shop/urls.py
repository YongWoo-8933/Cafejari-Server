
from django.urls import path, include
from rest_framework import routers
from shop.views import BrandViewSet, GifticonViewSet, ItemViewSet

router = routers.DefaultRouter()
router.register('brand', BrandViewSet)
router.register('item', ItemViewSet)
router.register('gifticon', GifticonViewSet)

urlpatterns = [
    path('', include(router.urls))
]