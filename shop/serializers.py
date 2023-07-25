
from rest_framework import serializers

from shop.models import Item, Coupon, UserCoupon, Gifticon


# 기본 serializer ------------------------------------------------------------------------
class ItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = Item
        fields = "__all__"


class GifticonSerializer(serializers.ModelSerializer):

    class Meta:
        model = Gifticon
        fields = "__all__"


class CouponSerializer(serializers.ModelSerializer):

    class Meta:
        model = Coupon
        fields = "__all__"


class UserCouponSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserCoupon
        fields = "__all__"



# 기본 serializer ------------------------------------------------------------------------
class UserCouponResponseSerializer(UserCouponSerializer):
    coupon = CouponSerializer(read_only=True)

    def to_representation(self, instance):
        self.fields['coupon'] = CouponSerializer(read_only=True)
        return super(UserCouponResponseSerializer, self).to_representation(instance)
