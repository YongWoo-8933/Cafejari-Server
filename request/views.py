from django.contrib.gis.geos import Point
from drf_yasg.utils import swagger_auto_schema, no_body
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from cafe.models import Cafe, District, CongestionArea, Brand
from cafe.serializers import CafeSerializer, CafeFloorSerializer, OpeningHourSerializer
from cafejari.settings import BASE_DOMAIN
from data.admin import OpeningHoursUpdateAdmin
from error import ServiceError
from notification.naver_sms import send_sms_to_admin
from request.models import CafeAdditionRequest, WithdrawalRequest, UserMigrationRequest, CafeInformationSuggestion, \
    AppFeedback
from request.serializers import CafeAdditionRequestResponseSerializer, CafeAdditionRequestSerializer, \
    WithdrawalRequestSerializer, UserMigrationRequestSerializer, CafeInformationSuggestionSerializer, \
    CafeInformationSuggestionRequestResponseSerializer, AppFeedbackSerializer
from request.swagger_serializers import SwaggerCafeAdditionRequestSerializer, SwaggerWithdrawalRequestSerializer, \
    SwaggerUserMigrationRequestSerializer, SwaggerCafeInformationSuggestionRequestSerializer, \
    SwaggerAppFeedbackRequestSerializer
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
                "point": Point(longitude, latitude, srid=4326),
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
                opening_hour_object = opening_hour_serializer.save()
                OpeningHoursUpdateAdmin.save_opening_hour(opening_hour_object=opening_hour_object)
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
            if not request.user.is_superuser:
                send_sms_to_admin(
                    content=f"카페 등록 요청 by {obj.user.profile.nickname}\n{obj.cafe.name}\nhttps://{BASE_DOMAIN}/admin/request/")

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
    queryset = CafeInformationSuggestion.objects.all()
    serializer_class = CafeInformationSuggestionRequestResponseSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_id='내 카페 정보 수정 요청 리스트',
        operation_description='내 카페 정보 수정 요청 리스트',
        request_body=no_body,
        responses={200: CafeInformationSuggestionRequestResponseSerializer(many=True)},
        manual_parameters=[AUTHORIZATION_MANUAL_PARAMETER]
    )
    def list(self, request, *args, **kwargs):
        return super(CafeInformationSuggestionViewSet, self).list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_id='카페 정보 수정 요청',
        operation_description='카페 정보 수정 요청',
        request_body=SwaggerCafeInformationSuggestionRequestSerializer,
        responses={201: CafeInformationSuggestionRequestResponseSerializer()},
        manual_parameters=[AUTHORIZATION_MANUAL_PARAMETER]
    )
    def create(self, request, *args, **kwargs):
        cafe_id = int(request.data.get("cafe_id"))
        is_closed = request.data.get("is_closed")
        top_floor = int(request.data.get("top_floor"))
        bottom_floor = int(request.data.get("bottom_floor"))
        opening_hour_list = request.data.get("opening_hour_list")
        wall_socket_rate_list = request.data.get("wall_socket_rate_list")
        restroom_list = request.data.get("restroom_list")
        no_seat_list = request.data.get("no_seat_list")
        latitude = request.data.get("latitude")
        longitude = request.data.get("longitude")
        etc = request.data.get("etc")
        description = ""

        try:
            # 정보 수정 요청한 원본 카페 찾기
            origin_cafe_object = Cafe.objects.get(id=cafe_id)

            # 수정 요청된 데이터를 바탕으로 suggested_cafe 생성
            cafe_data = {
                "is_visible": False,
                "name": f"정보수정요청_{request.user.profile.nickname}_{origin_cafe_object.name}",
                "address": origin_cafe_object.address
            }

            # 카페 오픈 여부
            if is_closed is not None:
                cafe_data["is_closed"] = bool(is_closed)
                description += "오픈여부 변경됨, "

            # 좌표 변경 여부
            if latitude is not None and longitude is not None:
                cafe_data["latitude"] = float(latitude)
                cafe_data["longitude"] = float(longitude)
                cafe_data["point"] = Point(longitude, latitude, srid=4326)
                description += "좌표 변경됨, "
            else:
                cafe_data["latitude"] = origin_cafe_object.latitude
                cafe_data["longitude"] = origin_cafe_object.longitude
                cafe_data["point"] = origin_cafe_object.point

            cafe_serializer = CafeSerializer(data=cafe_data)
            cafe_serializer.is_valid(raise_exception=True)
            suggested_cafe_object = cafe_serializer.save()

            # 층 정보 적용
            index = 0
            is_no_seat_changed = False
            is_wall_socket_rate_changed = False
            is_restroom_changed = False
            for floor in range(bottom_floor, top_floor + 1):
                if floor == 0: continue
                cafe_floor_data = {
                    "floor": floor,
                    "cafe": suggested_cafe_object.id
                }
                # 자리없는 층 정보 여부
                if no_seat_list is not None:
                    cafe_floor_data["has_seat"] = str(floor) not in no_seat_list
                    is_no_seat_changed = True
                # 콘센트 정보 변경 여부
                if wall_socket_rate_list is not None and wall_socket_rate_list[index]:
                    cafe_floor_data["wall_socket_rate"] = float(wall_socket_rate_list[index])
                    is_wall_socket_rate_changed = True
                # 화장실 정보 변경 여부
                if restroom_list is not None and restroom_list[index]:
                    cafe_floor_data["restroom"] = restroom_list[index]
                    is_restroom_changed = True
                cafe_floor_serializer = CafeFloorSerializer(data=cafe_floor_data)
                cafe_floor_serializer.is_valid(raise_exception=True)
                cafe_floor_serializer.save()
                index += 1
            if origin_cafe_object.cafe_floor.all().count() != index:
                description += "층 갯수 변경됨, "
            if is_no_seat_changed:
                description += "자리 없는 층 정보 변경됨, "
            if is_wall_socket_rate_changed:
                description += "콘센트 정보 변경됨, "
            if is_restroom_changed:
                description += "화장실 정보 변경됨, "

            # 오픈시간 변경 여부
            if opening_hour_list is not None:
                opening_hour_serializer = OpeningHourSerializer(data={
                    "cafe": suggested_cafe_object.id,
                    "mon": opening_hour_list[0],
                    "tue": opening_hour_list[1],
                    "wed": opening_hour_list[2],
                    "thu": opening_hour_list[3],
                    "fri": opening_hour_list[4],
                    "sat": opening_hour_list[5],
                    "sun": opening_hour_list[6]
                })
                opening_hour_serializer.is_valid(raise_exception=True)
                opening_hour_object = opening_hour_serializer.save()
                OpeningHoursUpdateAdmin.save_opening_hour(opening_hour_object=opening_hour_object)
                description += "오픈시간 변경됨, "

            # request 작성
            cafe_suggestion_request_serializer = CafeInformationSuggestionSerializer(data={
                "user": request.user.id,
                "cafe": origin_cafe_object.id,
                "suggested_cafe": suggested_cafe_object.id,
                "etc": etc,
                "description": description
            })
            cafe_suggestion_request_serializer.is_valid(raise_exception=True)
            obj = cafe_suggestion_request_serializer.save()

            # 관리자에게 요청 알림
            if not request.user.is_superuser:
                send_sms_to_admin(
                    content=f"카페 정보수정 요청 by {obj.user.profile.nickname}\n{obj.cafe.name}\nhttps://{BASE_DOMAIN}/admin/request/")

            return Response(data=self.get_serializer(obj, read_only=True).data, status=status.HTTP_201_CREATED)
        except Cafe.DoesNotExist:
            return ServiceError.no_cafe_response()

    @swagger_auto_schema(
        operation_id='카페 정보 수정 요청 삭제',
        operation_description='내가 했던 카페 정보 수정 요청 삭제',
        request_body=no_body,
        responses={204: ""},
        manual_parameters=[AUTHORIZATION_MANUAL_PARAMETER]
    )
    def destroy(self, request, *args, **kwargs):
        return super(CafeInformationSuggestionViewSet, self).destroy(request, *args, **kwargs)


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
        # 관리자에게 요청 알림
        if not request.user.is_superuser:
            send_sms_to_admin(
                content=f"회원 탈퇴 요청 by {request.user.profile.nickname}\nhttps://{BASE_DOMAIN}/admin/request/")
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

            # 관리자에게 요청 알림
            if not request.user.is_superuser:
                send_sms_to_admin(
                    content=f"사용자 정보 이전 요청 by {request.user.profile.nickname}\n번호: {phone_number}\nhttps://{BASE_DOMAIN}/admin/request/")
            return Response(data=request_serializer.data,status=status.HTTP_201_CREATED)


class AppFeedbackViewSet(
    GenericViewSet
):
    queryset = AppFeedback.objects.all()
    serializer_class = AppFeedbackSerializer
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_id='게스트 유저 피드백 제출',
        operation_description='인증 정보가 없는 게스트 유저의 앱 피드백 제출',
        request_body=SwaggerAppFeedbackRequestSerializer,
        responses={201: AppFeedbackSerializer()}
    )
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def guest_feedback(self, request):
        feedback = str(request.data.get("feedback"))

        serializer = self.get_serializer(data={"feedback": feedback})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        operation_id='유저 피드백 제출',
        operation_description='로그인한 유저의 앱 피드백 제출',
        request_body=SwaggerAppFeedbackRequestSerializer,
        responses={201: AppFeedbackSerializer()}
    )
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def user_feedback(self, request):
        feedback = str(request.data.get("feedback"))

        serializer = self.get_serializer(data={"feedback": feedback, "user": request.user.id})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)
