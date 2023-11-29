
from django.urls import path, include
from rest_framework import routers
from shop.views import BrandViewSet, GifticonViewSet, ItemViewSet, CouponViewSet, UserCouponViewSet

router = routers.DefaultRouter()
router.register('brand', BrandViewSet)
router.register('item', ItemViewSet)
router.register('gifticon', GifticonViewSet)
router.register('coupon', CouponViewSet)
router.register('user_coupon', UserCouponViewSet)

urlpatterns = [
    path('', include(router.urls))
]