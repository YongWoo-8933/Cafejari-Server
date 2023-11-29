
from rest_framework import serializers

from shop.models import Item, Coupon, UserCoupon, Gifticon


# 기본 serializer ------------------------------------------------------------------------
from utils import ImageModelSerializer


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
# 기프티콘 이미지 응답용 serializer
class GifticonResponseSerializer(ImageModelSerializer):
    description = serializers.SerializerMethodField(read_only=True)

    @staticmethod
    def get_description(obj):
        return obj.item.description

    class Meta:
        model = Gifticon
        fields = "__all__"


# 쿠폰 이미지 응답용 serializer
class CouponResponseSerializer(ImageModelSerializer):

    class Meta:
        model = Coupon
        fields = "__all__"


# 유저 쿠폰 응답용 serializer
class UserCouponResponseSerializer(UserCouponSerializer):
    coupon = CouponResponseSerializer(read_only=True)

    def to_representation(self, instance):
        self.fields['coupon'] = CouponResponseSerializer(read_only=True)
        return super(UserCouponResponseSerializer, self).to_representation(instance)
