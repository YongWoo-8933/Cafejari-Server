from drf_yasg.utils import swagger_auto_schema, no_body
from rest_framework import mixins, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from cafe.models import Cafe, District, CongestionArea, Brand
from cafe.serializers import CafeSerializer, CafeFloorSerializer, OpeningHourSerializer
from error import ServiceError
from notification.naver_sms import send_sms_to_admin
from request.models import CafeAdditionRequest, WithdrawalRequest, UserMigrationRequest
from request.serializers import CafeAdditionRequestResponseSerializer, CafeAdditionRequestSerializer, \
    WithdrawalRequestSerializer, UserMigrationRequestSerializer
from request.swagger_serializers import SwaggerCafeAdditionRequestSerializer, SwaggerWithdrawalRequestSerializer, \
    SwaggerUserMigrationRequestSerializer
from user.serializers import UserSerializer
from utils import UserListDestroyViewSet, AUTHORIZATION_MANUAL_PARAMETER


class CafeAdditionRequestViewSet(
    mixins.CreateModelMixin,
    UserListDestroyViewSet
):
    queryset = CafeAdditionRequest.objects.all()
    serializer_class = CafeAdditionRequestResponseSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_id='내 카페 등록요청 리스트',
        operation_description='내가 등록 요청한 카페 리스트',
        request_body=no_body,
        responses={200: CafeAdditionRequestResponseSerializer(many=True)},
        manual_parameters=[AUTHORIZATION_MANUAL_PARAMETER]
    )
    def list(self, request, *args, **kwargs):
        return super(CafeAdditionRequestViewSet, self).list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_id='카페 추가 요청',
        operation_description='새로운 카페 추가 요청, no_seat_floor_list에는 자리가 없는 층을 int or str list로 전송',
        request_body=SwaggerCafeAdditionRequestSerializer,
        responses={201: CafeAdditionRequestResponseSerializer()},
        manual_parameters=[AUTHORIZATION_MANUAL_PARAMETER]
    )
    def create(self, request, *args, **kwargs):
        cafe_name = request.data.get("cafe_name")
        dong_address = request.data.get("dong_address")
        road_address = request.data.get("road_address")
        latitude = float(request.data.get("latitude"))
        longitude = float(request.data.get("longitude"))
        top_floor = int(request.data.get("top_floor"))
        bottom_floor = int(request.data.get("bottom_floor"))
        wall_socket_rate_list = request.data.get("wall_socket_rate_list")
        opening_hour_list = request.data.get("opening_hour_list")
        etc = request.data.get("etc")

        try:
            Cafe.objects.get(name=cafe_name, address=road_address)
            return ServiceError.duplicated_cafe_response()
        except Cafe.DoesNotExist:
            # district 체크
            dong_address_list = dong_address.split()
            road_address_list = road_address.split()
            districts = District.objects.filter(gu__in=road_address_list, dong__in=dong_address_list)

            # congestion area 체크
            congestion_areas = CongestionArea.objects.filter(
                south_west_latitude__lt=latitude,
                south_west_longitude__lt=longitude,
                north_east_latitude__gt=latitude,
                north_east_longitude__gt=longitude
            )
            congestion_area_id_list = [congestion_area.id for congestion_area in congestion_areas]

            # brand 체크
            brand = None
            for brand_object in Brand.objects.all():
                if brand_object.name in cafe_name:
                    brand = brand_object
                    break

            cafe_data = {
                "is_visible": False,
                "name": cafe_name,
                "address": road_address,
                "latitude": latitude,
                "longitude": longitude,
                "congestion_area": congestion_area_id_list,
            }
            if districts: cafe_data["district"] = districts[0].id
            if brand: cafe_data["brand"] = brand.id

            cafe_serializer = CafeSerializer(data=cafe_data)
            cafe_serializer.is_valid(raise_exception=True)
            new_cafe_object = cafe_serializer.save()

            # cafe floor 생성
            index = 0
            for floor in range(bottom_floor, top_floor+1):
                if floor == 0: continue
                cafe_floor_serializer = CafeFloorSerializer(data={
                    "floor": floor,
                    "wall_socket_rate": float(wall_socket_rate_list[index]) if wall_socket_rate_list else None,
                    "cafe": new_cafe_object.id
                })
                cafe_floor_serializer.is_valid(raise_exception=True)
                cafe_floor_serializer.save()
                index += 1

            # opening hour 설정
            if opening_hour_list:
                opening_hour_serializer = OpeningHourSerializer(data={
                    "mon": opening_hour_list[0],
                    "tue": opening_hour_list[1],
                    "wed": opening_hour_list[2],
                    "thu": opening_hour_list[3],
                    "fri": opening_hour_list[4],
                    "sat": opening_hour_list[5],
                    "sun": opening_hour_list[6],
                    "cafe": new_cafe_object.id
                })
                opening_hour_serializer.is_valid(raise_exception=True)
                opening_hour_serializer.save()

            # request 작성
            cafe_addition_request_serializer = CafeAdditionRequestSerializer(data={
                "user": request.user.id,
                "cafe": new_cafe_object.id,
                "etc": etc if etc else None
            })
            cafe_addition_request_serializer.is_valid(raise_exception=True)
            obj = cafe_addition_request_serializer.save()

            # 관리자에게 요청 알림
            send_sms_to_admin(
                content=f"카페 등록 요청 by {obj.user.profile.nickname}\n{obj.cafe.name}\nhttp://localhost/admin/request/")

            return Response(data=self.get_serializer(obj, read_only=True).data, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        operation_id='카페 등록 요청 삭제',
        operation_description='내가 했던 카페 등록 요청 삭제',
        request_body=no_body,
        responses={204: ""},
        manual_parameters=[AUTHORIZATION_MANUAL_PARAMETER]
    )
    def destroy(self, request, *args, **kwargs):
        return super(CafeAdditionRequestViewSet, self).destroy(request, *args, **kwargs)


class CafeInformationSuggestionViewSet(
    mixins.CreateModelMixin,
    UserListDestroyViewSet
):
    queryset = CafeAdditionRequest.objects.all()
    serializer_class = CafeAdditionRequestResponseSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        cafe_id = request.data.get("cafe_id")
        is_opened = request.data.get("is_opened")
        opening_hour = request.data.get("opening_hour")
        restroom = request.data.get("restroom")
        wall_socket_rate = request.data.get("wall_socket_rate")
        no_seat_floor_list = request.data.get("no_seat_floor_list")
        tag_id_list = request.data.get("tag_id_list")
        total_floor = request.data.get("total_floor")
        first_floor = request.data.get("first_floor")
        image = request.FILES.get('file_key')


        # return Response(data=cafe_addition_request_serializer.data, status=status.HTTP_201_CREATED)


class WithdrawalRequestViewSet(
    mixins.CreateModelMixin,
    GenericViewSet
):
    queryset = WithdrawalRequest.objects.all()
    serializer_class = WithdrawalRequestSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_id='회원탈퇴 요청',
        operation_description='회원 탈퇴 요청, 탈퇴 사유 받고 유저 비활성화',
        request_body=SwaggerWithdrawalRequestSerializer,
        responses={204: ""},
        manual_parameters=[AUTHORIZATION_MANUAL_PARAMETER]
    )
    def create(self, request, *args, **kwargs):
        request_serializer = self.get_serializer(data={"reason": request.data.get("reason"), "user": request.user.id})
        request_serializer.is_valid(raise_exception=True)
        request_serializer.save()
        user_serializer = UserSerializer(request.user, data={"is_active": False}, partial=True)
        user_serializer.is_valid(raise_exception=True)
        user_serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserMigrationRequestViewSet(
    mixins.CreateModelMixin,
    GenericViewSet
):
    queryset = UserMigrationRequest.objects.all()
    serializer_class = UserMigrationRequestSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_id='사용자 정보 이전 요청',
        operation_description='이전 버전 유저의 사용자 정보 이전요청',
        request_body=SwaggerUserMigrationRequestSerializer,
        responses={201: UserMigrationRequestSerializer()},
        manual_parameters=[AUTHORIZATION_MANUAL_PARAMETER]
    )
    def create(self, request, *args, **kwargs):
        phone_number = request.data.get("phone_number")
        try:
            request_object = self.queryset.get(phone_number=phone_number, user=request.user.id)
            if request_object.is_completed:
                return ServiceError.already_completed_user_migration_response()
            else:
                return ServiceError.duplicated_user_migration_response()
        except UserMigrationRequest.DoesNotExist:
            request_serializer = self.get_serializer(data={"phone_number": phone_number, "user": request.user.id})
            request_serializer.is_valid(raise_exception=True)
            request_serializer.save()
            return Response(data=request_serializer.data,status=status.HTTP_201_CREATED)
