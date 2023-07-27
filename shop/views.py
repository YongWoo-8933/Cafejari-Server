import datetime
import os
import time

import requests
from django.core.files.base import ContentFile
from drf_yasg.utils import swagger_auto_schema, no_body
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from cafe.models import Brand
from error import ServiceError
from notification.naver_sms import send_sms_to_admin
from shop.giftishow_biz import GiftishowBiz
from shop.models import Item, Gifticon, Coupon, UserCoupon
from cafe.serializers import BrandSerializer
from shop.serializers import ItemSerializer, GifticonSerializer, CouponSerializer, UserCouponResponseSerializer, \
    GifticonResponseSerializer, CouponResponseSerializer
from shop.swagger_serializers import SwaggerGifticonRequestSerializer
from user.serializers import ProfileResponseSerializer, ProfileSerializer
from utils import UserListDestroyViewSet, AUTHORIZATION_MANUAL_PARAMETER


class BrandViewSet(
    mixins.ListModelMixin,
    GenericViewSet
):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    permission_classes = [AllowAny]

    def filter_queryset(self, queryset):
        return queryset.filter(has_item=True)

    @swagger_auto_schema(
        operation_id='상점 브랜드',
        operation_description='상점에 표시할 브랜드 리스트',
        request_body=no_body,
        responses={200: BrandSerializer(many=True)},
    )
    def list(self, request, *args, **kwargs):
        return super(BrandViewSet, self).list(request, *args, **kwargs)


class ItemViewSet(
    mixins.ListModelMixin,
    GenericViewSet
):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_id='아이템',
        operation_description='상점에서 판매하는 아이템 리스트',
        request_body=no_body,
        responses={200: ItemSerializer(many=True)},
    )
    def list(self, request, *args, **kwargs):
        return super(ItemViewSet, self).list(request, *args, **kwargs)


class GifticonViewSet(
    mixins.CreateModelMixin,
    UserListDestroyViewSet
):
    queryset = Gifticon.objects.all()
    serializer_class = GifticonResponseSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_id='기프티콘 리스트',
        operation_description='유저가 구매한 기프티콘 리스트(사용 완료 포함)',
        request_body=no_body,
        responses={200: GifticonResponseSerializer(many=True)},
        manual_parameters=[AUTHORIZATION_MANUAL_PARAMETER]
    )
    def list(self, request, *args, **kwargs):
        return super(GifticonViewSet, self).list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_id='기프티콘 구매',
        operation_description='상점에서 기프티콘 구매',
        request_body=SwaggerGifticonRequestSerializer,
        responses={200: GifticonSerializer(many=True)},
        manual_parameters=[AUTHORIZATION_MANUAL_PARAMETER]
    )
    def create(self, request, *args, **kwargs):
        item_id = int(request.data.get("item_id"))
        # 아이템 유무
        try:
            item_object = Item.objects.get(id=item_id)
        except Item.DoesNotExist:
            return ServiceError.no_item_response()

        # 포인트 부족 여부
        if item_object.price > request.user.profile.point:
            return ServiceError.not_enough_point_response()

        # mms 발송요청
        tr_id, response = GiftishowBiz.send_gifticon(goods_code=item_object.code)
        print(tr_id)
        if not response:
            return ServiceError.gifticon_send_failure_response()
        if response.status_code != 200:
            return ServiceError.gifticon_send_failure_response()

        gifticon_image_url = response.json()['result']['result']['couponImgUrl']
        image_response = requests.get(gifticon_image_url, stream=True)
        temp_file_name = f"{tr_id}_gifticon.jpg"

        # 임시 파일 생성후 저장
        if image_response.status_code == 200:
            with open(temp_file_name, 'wb') as file:
                for chunk in image_response.iter_content(1024):
                    file.write(chunk)
        time.sleep(0.4)
        with open(temp_file_name, 'rb') as f:
            image = ContentFile(f.read(), name=temp_file_name)
        serializer = GifticonSerializer(data={
            "image": image,
            "expiration_period": datetime.datetime.now() + datetime.timedelta(days=30),
            "is_used": False,
            "item": item_id,
            "user": request.user.id,
            "tr_id": tr_id
        })
        serializer.is_valid(raise_exception=True)
        serializer.save()
        os.remove(temp_file_name)

        # 포인트 정산
        profile_serializer = ProfileSerializer(request.user.profile,
                                               data={"point": request.user.profile.point - item_object.price},
                                               partial=True)
        profile_serializer.is_valid(raise_exception=True)
        profile_serializer.save()

        # 발송 성공 후 비즈머니 체크 로직
        balance = GiftishowBiz.get_biz_money_balance()
        if balance:
            if balance < 40000:
                send_sms_to_admin(content=f"현재 남은 비즈머니가 {balance}원입니다. 충전해주세요.")
        else:
            send_sms_to_admin(content=f"상품 구매 후 비즈머니 충전금 조회에 실패했습니다")

        return Response(data=serializer.data, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        operation_id='기프티콘 삭제',
        operation_description='사용 완료한 기프티콘 삭제(사용 완료가 아니면 에러)',
        request_body=no_body,
        responses={204: ""},
        manual_parameters=[AUTHORIZATION_MANUAL_PARAMETER]
    )
    def destroy(self, request, *args, **kwargs):
        if not self.get_object().is_used:
            return ServiceError.gifticon_delete_failure_response()
        return super(GifticonViewSet, self).destroy(request, *args, **kwargs)

    @swagger_auto_schema(
        method='put',
        operation_id='기프티콘 사용처리',
        operation_description='기프티콘 사용 완료 처리',
        request_body=no_body,
        responses={201: GifticonResponseSerializer()},
        manual_parameters=[AUTHORIZATION_MANUAL_PARAMETER]
    )
    @action(methods=['put'], detail=True, )
    def use(self, request, *args, **kwargs):
        gifticon_object = self.get_object()
        if gifticon_object.user.id != request.user.id:
            return ServiceError.unauthorized_user_response()
        serializer = self.get_serializer(gifticon_object, data={"is_used": True}, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)


class CouponViewSet(
    mixins.ListModelMixin,
    GenericViewSet
):
    queryset = Coupon.objects.all()
    serializer_class = CouponResponseSerializer
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_id='쿠폰 리스트',
        operation_description='유저가 사용할 수 있는 모든 쿠폰 리스트',
        request_body=no_body,
        responses={200: CouponSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super(CouponViewSet, self).list(request, *args, **kwargs)


class UserCouponViewSet(UserListDestroyViewSet):
    queryset = UserCoupon.objects.all()
    serializer_class = UserCouponResponseSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_id='유저 쿠폰 리스트',
        operation_description='자신이 가지고 있는 모든 쿠폰 리스트',
        request_body=no_body,
        responses={200: CouponSerializer(many=True)},
        manual_parameters=[AUTHORIZATION_MANUAL_PARAMETER]
    )
    def list(self, request, *args, **kwargs):
        return super(UserCouponViewSet, self).list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_id='유저 쿠폰 삭제',
        operation_description='유저가 가지고 있는 쿠폰 삭제',
        request_body=no_body,
        responses={204: ""},
        manual_parameters=[AUTHORIZATION_MANUAL_PARAMETER]
    )
    def destroy(self, request, *args, **kwargs):
        return super(UserCouponViewSet, self).destroy(request, *args, **kwargs)


