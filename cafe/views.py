import datetime

from django.db.models import Q
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema, no_body
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from cafe.models import Cafe, CafeFloor, OccupancyRateUpdateLog, DailyActivityStack
from cafe.serializers import CafeResponseSerializer, \
    OccupancyRateUpdateLogResponseSerializer, OccupancyRateUpdateLogSerializer, DailyActivityStackSerializer, \
    CafeSearchResponseSerializer
from cafe.swagger_serializers import SwaggerOccupancyRegistrationRequestSerializer, SwaggerCafeResponseSerializer
from cafejari.settings import UPDATE_COOLTIME, OCCUPANCY_INSUFFICIENT_THRESHOLD, OCCUPANCY_ENOUGH_THRESHOLD, \
    ENOUGH_DATA_POINT, INSUFFICIENT_DATA_POINT, NO_DATA_POINT
from error import ServiceError
from utils import AUTHORIZATION_MANUAL_PARAMETER


class CafePagination(PageNumberPagination):
    page_size = 30
    max_page_size = 500


class CafeViewSet(
    mixins.ListModelMixin,
    GenericViewSet
):
    queryset = Cafe.objects.all()
    serializer_class = CafeResponseSerializer
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_id='카페 지도 정보',
        operation_description='지도에서 받을 카페 리스트 정보를 받음',
        responses={200: SwaggerCafeResponseSerializer(many=True)},
        manual_parameters=[
            openapi.Parameter(
                name='latitude',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_NUMBER,
                required=False,
                description='float값, default=신촌위도',
            ),
            openapi.Parameter(
                name='longitude',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_NUMBER,
                required=False,
                description='float값, default=신촌경도',
            ),
            openapi.Parameter(
                name='zoom_level',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_INTEGER,
                required=False,
                description='1, 2, 3 int 값으로. default=3',
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        latitude = float(self.request.query_params.get('latitude') or 37.55649747287372)
        longitude = float(self.request.query_params.get('longitude') or 126.93710302643744)
        zoom_level = int(self.request.query_params.get('zoom_level') or 3)

        latitude_bound = 0.01 * zoom_level
        longitude_bound = 0.012 * zoom_level

        queryset = self.queryset.filter(
            is_visible=True,
            is_closed=False,
            latitude__range=(latitude - latitude_bound, latitude + latitude_bound),
            longitude__range=(longitude - longitude_bound, longitude + longitude_bound)
        )
        return Response(data=self.get_serializer(queryset, many=True).data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_id='카페 검색 정보',
        operation_description='검색 했을 때 카페 이름+주소 정보를 받음',
        responses={200: CafeSearchResponseSerializer(many=True)},
        manual_parameters=[
            openapi.Parameter(
                name='query',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                required=True,
                description='검색어',
            )
        ]
    )
    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def search(self, queryset):
        query = self.request.query_params.get('query')
        queryset = self.queryset.filter(is_closed=False, is_visible=True)
        if query:
            query_list = query.split()
            for query_word in query_list:
                queryset = queryset.filter(Q(name__icontains=query_word) | Q(address__icontains=query_word))

        serializer = CafeSearchResponseSerializer(queryset)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    # @swagger_auto_schema(
    #     operation_id='카페 검색 정보',
    #     operation_description='검색 했을 때 카페 리스트 정보를 받음',
    #     responses={200: SwaggerCafeSearchResponseSerializer(many=True)},
    #     manual_parameters=[
    #         openapi.Parameter(
    #             name='query',
    #             in_=openapi.IN_QUERY,
    #             type=openapi.TYPE_STRING,
    #             required=True,
    #             description='검색어',
    #         ),
    #         openapi.Parameter(
    #             name='page',
    #             in_=openapi.IN_QUERY,
    #             type=openapi.TYPE_INTEGER,
    #             required=False,
    #             description='몇 번째 페이지를 조회할지, default=1',
    #         ),
    #     ]
    # )
    # @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    # def search(self, queryset):
    #     query = self.request.query_params.get('query')
    #     queryset = self.queryset.filter(is_closed=False, is_visible=True)
    #     if query:
    #         query_list = query.split()
    #         for query_word in query_list:
    #             queryset = queryset.filter(Q(name__icontains=query_word) | Q(address__icontains=query_word))
    #
    #     paginator = CafePagination()
    #     page = paginator.paginate_queryset(queryset, self.request)
    #     serializer = self.get_serializer(page, many=True)
    #     return paginator.get_paginated_response(data=serializer.data)


class OccupancyRateUpdateLogViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    GenericViewSet
):
    queryset = OccupancyRateUpdateLog.objects.all()
    serializer_class = OccupancyRateUpdateLogResponseSerializer
    permission_classes = [IsAuthenticated]

    @staticmethod
    def save_log(occupancy_rate, cafe_floor_id, user_id, point):
        occupancy_rate_update_log_data = {
            "occupancy_rate": occupancy_rate,
            "cafe_floor": cafe_floor_id,
            "user": user_id,
            "point": point
        }
        serializer = OccupancyRateUpdateLogSerializer(data=occupancy_rate_update_log_data)
        serializer.is_valid(raise_exception=True)
        return serializer.save()

    @swagger_auto_schema(
        operation_id='게스트 유저 혼잡도 등록',
        operation_description='인증 정보가 없는 게스트 유저의 혼잡도 등록, 응답 user는 null 고정',
        request_body=SwaggerOccupancyRegistrationRequestSerializer,
        responses={201: OccupancyRateUpdateLogResponseSerializer()}
    )
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def guest_registration(self, request):
        occupancy_rate = float(request.data.get("occupancy_rate"))
        cafe_floor_id = int(request.data.get("cafe_floor_id"))

        # cafe_floor의 유효성 검사
        try:
            cafe_floor_object = CafeFloor.objects.get(id=cafe_floor_id)
            if not cafe_floor_object.has_seat:
                return ServiceError.no_cafe_seat_response()
        except CafeFloor.DoesNotExist:
            return ServiceError.no_cafe_floor_response()

        # occupancy_rate_update_log 작성
        saved_object = self.save_log(occupancy_rate=occupancy_rate, cafe_floor_id=cafe_floor_id, user_id=None, point=0)

        return Response(self.get_serializer(saved_object, read_only=True).data, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        operation_id='내 활동 이력',
        operation_description='내 혼잡도 등록 활동 모두 보기',
        request_body=no_body,
        responses={200: OccupancyRateUpdateLogResponseSerializer(many=True)},
        manual_parameters=[AUTHORIZATION_MANUAL_PARAMETER]
    )
    def list(self, request, *args, **kwargs):
        queryset = self.queryset.filter(user__id=request.user.id)
        return Response(data=self.get_serializer(queryset, many=True).data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_id='유저 혼잡도 등록',
        operation_description='로그인한 유저의 혼잡도 등록',
        request_body=SwaggerOccupancyRegistrationRequestSerializer,
        responses={201: OccupancyRateUpdateLogResponseSerializer()},
        manual_parameters=[AUTHORIZATION_MANUAL_PARAMETER]
    )
    def create(self, request, *args, **kwargs):
        occupancy_rate = float(request.data.get("occupancy_rate"))
        cafe_floor_id = int(request.data.get("cafe_floor_id"))

        # cafe_floor의 유효성 검사
        try:
            cafe_floor_object = CafeFloor.objects.get(id=cafe_floor_id)
            if not cafe_floor_object.has_seat:
                return ServiceError.no_cafe_seat_response()
        except CafeFloor.DoesNotExist:
            return ServiceError.no_cafe_floor_response()

        # 포인트 상세 로직
        now = datetime.datetime.now()
        midnight = datetime.datetime(year=now.year, month=now.month, day=now.day, hour=0, minute=0, second=1)
        today_this_cafe_update_logs = OccupancyRateUpdateLog.objects.filter(
            update__gte=midnight, cafe_floor__id=cafe_floor_id, user__id=request.user.id)

        if today_this_cafe_update_logs:
            # 오늘 이 카페에서 활동 이력 있음
            # 쿨타임 확인, 아직 안지났으면 에러
            recent_update_log = today_this_cafe_update_logs.order_by("-update")[0]
            if (now - recent_update_log.update).total_seconds() < UPDATE_COOLTIME * 60:
                return ServiceError.update_cooltime_response()

            # 오늘 이 카페에서 업데이트한 횟수 확인
            count_restriction = request.user.profile.grade.sharing_restriction_per_cafe
            if today_this_cafe_update_logs.count() > count_restriction:
                saved_object = self.save_log(occupancy_rate=occupancy_rate, cafe_floor_id=cafe_floor_id,
                                     user_id=request.user.id, point=0)
                return Response(self.get_serializer(saved_object, read_only=True).data, status=status.HTTP_201_CREATED)
        else:
            # 오늘 이 카페에서 활동 이력 없음
            stack_restriction = request.user.profile.grade.activity_stack_restriction_per_day
            today_other_cafe_stacks = DailyActivityStack.objects.filter(update__gte=midnight)
            if today_other_cafe_stacks.count() >= stack_restriction:
                # stack 초과(포인트 지급 불가)
                saved_object = self.save_log(occupancy_rate=occupancy_rate, cafe_floor_id=cafe_floor_id,
                                     user_id=request.user.id, point=0)
                return Response(self.get_serializer(saved_object, read_only=True).data, status=status.HTTP_201_CREATED)
            else:
                # stack 하나 쌓기
                stack_serializer = DailyActivityStackSerializer(data={"user": request.user.id, "cafe_floor": cafe_floor_id})
                stack_serializer.is_valid(raise_exception=True)
                stack_serializer.save()
        # 카페의 데이터 충분 여부 판단
        count = OccupancyRateUpdateLog.objects.filter(cafe_floor__id=cafe_floor_id).count()
        if count < OCCUPANCY_INSUFFICIENT_THRESHOLD:
            point = NO_DATA_POINT
        elif count < OCCUPANCY_ENOUGH_THRESHOLD:
            point = INSUFFICIENT_DATA_POINT
        else:
            point = ENOUGH_DATA_POINT

        # occupancy_rate_update_log 작성
        saved_object = self.save_log(occupancy_rate=occupancy_rate, cafe_floor_id=cafe_floor_id,
                                     user_id=request.user.id, point=point)

        return Response(self.get_serializer(saved_object, read_only=True).data,
                        status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        operation_id='최근 30분 내 업데이트',
        operation_description='내가 한 최근 30분 동안의 모든 혼잡도 업데이트 정보',
        responses={201: OccupancyRateUpdateLogResponseSerializer(many=True)},
        manual_parameters=[AUTHORIZATION_MANUAL_PARAMETER]
    )
    @action(methods=['get'], detail=False)
    def recent_updated_log(self, request):
        now = datetime.datetime.now()
        recent_updated_logs = self.queryset.filter(user__id=request.user.id, update__gt=now - datetime.timedelta(minutes=30))
        return Response(data=self.get_serializer(recent_updated_logs, many=True).data, status=status.HTTP_200_OK)
