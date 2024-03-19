import datetime

from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import Point, GEOSGeometry
from django.db.models import Q
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema, no_body
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from cafe.models import Cafe, CafeFloor, OccupancyRateUpdateLog, DailyActivityStack, Location, CATI, Congestion, \
    OccupancyRatePrediction
from cafe.serializers import CafeResponseSerializer, \
    OccupancyRateUpdateLogResponseSerializer, OccupancyRateUpdateLogSerializer, DailyActivityStackSerializer, \
    CafeSearchResponseSerializer, LocationResponseSerializer, CATISerializer
from cafe.swagger_serializers import SwaggerOccupancyRegistrationRequestSerializer, SwaggerCafeResponseSerializer, \
    SwaggerCATIRequestSerializer
from cafe.utils import PointCalculator
from cafejari.settings import UPDATE_COOLTIME, RECENT_HOUR
from challenge.models import Challenge
from cron.occupancy_prediction import is_occupancy_update_possible
from error import ServiceError
from notification.firebase_message import FirebaseMessage
from notification.models import PushNotificationType
from user.serializers import ProfileSerializer
from utils import AUTHORIZATION_MANUAL_PARAMETER


class CafePagination(PageNumberPagination):
    page_size = 30
    max_page_size = 500


class CafeViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
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
        zoom_level = int(self.request.query_params.get('zoom_level') or 1)

        latitude_bound = 0.01 * 0.7 * zoom_level
        longitude_bound = 0.012 * 0.35 * zoom_level

        queryset = self.queryset.filter(
            is_visible=True,
            is_closed=False,
            latitude__gte=latitude - latitude_bound,
            latitude__lte=latitude + latitude_bound,
            longitude__gte=longitude - longitude_bound,
            longitude__lte=longitude + longitude_bound,
        )
        return Response(data=self.get_serializer(queryset, many=True).data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_id='개별 카페 정보',
        operation_description='카페 id를 통해 개별 카페 정보를 받음',
        responses={200: SwaggerCafeResponseSerializer()},
    )
    def retrieve(self, request, *args, **kwargs):
        return super(CafeViewSet, self).retrieve(request, *args, **kwargs)

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
            ),
            openapi.Parameter(
                name='latitude',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_NUMBER,
                required=False,
                description='위도',
            ),
            openapi.Parameter(
                name='longitude',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_NUMBER,
                required=False,
                description='경도',
            )
        ]
    )
    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def search(self, queryset):
        query = self.request.query_params.get('query')
        latitude = self.request.query_params.get('latitude')
        longitude = self.request.query_params.get('longitude')
        queryset = self.queryset.filter(is_closed=False, is_visible=True)
        if query:
            query_list = query.split()
            for query_word in query_list:
                queryset = queryset.filter(Q(name__icontains=query_word) | Q(address__icontains=query_word))
        if latitude and longitude:
            user_location = Point(float(longitude), float(latitude), srid=4326)
            queryset = queryset.annotate(
                distance=Distance("point", GEOSGeometry(user_location, srid=4326))
            ).order_by("distance")
        if len(queryset) > 300:
            queryset = queryset[:300]
        serializer = CafeSearchResponseSerializer(queryset, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_id='카페 추천(거리순)',
        operation_description='거리가 가까운 순으로 카페 추천',
        responses={200: CafeSearchResponseSerializer(many=True)},
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
        ]
    )
    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def recommendation(self, queryset):
        latitude = float(self.request.query_params.get('latitude') or 37.55649747287372)
        longitude = float(self.request.query_params.get('longitude') or 126.93710302643744)

        # 사용자 위치를 Point 객체로 생성
        user_location = Point(longitude, latitude, srid=4326)

        # 거리순 카페 정렬
        cafes = Cafe.objects.annotate(
            distance=Distance("point", GEOSGeometry(user_location, srid=4326))
        ).order_by("distance")

        # 뺄 카페 거르기
        cafes = cafes.filter(is_visible=True, is_closed=False, is_opened=True)[:20]

        return Response(data=self.get_serializer(cafes, many=True).data, status=status.HTTP_200_OK)


class OccupancyRateUpdateLogViewSet(
    mixins.ListModelMixin,
    GenericViewSet
):
    queryset = OccupancyRateUpdateLog.objects.all()
    serializer_class = OccupancyRateUpdateLogResponseSerializer
    permission_classes = [IsAuthenticated]

    @staticmethod
    def save_log(occupancy_rate, cafe_floor_id, user_id, point, congestion):
        occupancy_rate_update_log_data = {
            "occupancy_rate": occupancy_rate,
            "cafe_floor": cafe_floor_id,
            "user": user_id,
            "point": point,
            "congestion": congestion
        }
        serializer = OccupancyRateUpdateLogSerializer(data=occupancy_rate_update_log_data)
        serializer.is_valid(raise_exception=True)
        return serializer.save()

    @staticmethod
    def get_congestion(cafe_floor_object):
        if cafe_floor_object.cafe.congestion_area.all():
            current_congestion_index = 0
            for lookup_congestion_area in cafe_floor_object.cafe.congestion_area.all():
                temp_congestion_index = list(Congestion).index(Congestion(lookup_congestion_area.current_congestion))
                if current_congestion_index < temp_congestion_index:
                    current_congestion_index = temp_congestion_index
            return list(Congestion)[current_congestion_index].value
        else:
            return None

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

        # 혼잡도 업데이트 금지시간 확인
        if not is_occupancy_update_possible():
            return ServiceError.update_forbidden_time_response()

        # 카페 오픈 유무 확인
        if not cafe_floor_object.cafe.is_opened:
            return ServiceError.cafe_closed_response()

        # 지역 혼잡도 가져오기
        congestion = self.get_congestion(cafe_floor_object)

        # occupancy_rate_update_log 작성
        saved_object = self.save_log(
            occupancy_rate=occupancy_rate,
            cafe_floor_id=cafe_floor_id,
            user_id=None,
            point=0,
            congestion=congestion
        )

        return Response(self.get_serializer(saved_object, read_only=True).data, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        operation_id='유저 혼잡도 등록',
        operation_description='로그인한 유저의 혼잡도 등록',
        request_body=SwaggerOccupancyRegistrationRequestSerializer,
        responses={201: OccupancyRateUpdateLogResponseSerializer()},
        manual_parameters=[AUTHORIZATION_MANUAL_PARAMETER]
    )
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def user_registration(self, request):
        occupancy_rate = float(request.data.get("occupancy_rate"))
        cafe_floor_id = int(request.data.get("cafe_floor_id"))

        # cafe_floor의 유효성 검사
        try:
            cafe_floor_object = CafeFloor.objects.get(id=cafe_floor_id)
            if not cafe_floor_object.has_seat:
                return ServiceError.no_cafe_seat_response()
        except CafeFloor.DoesNotExist:
            return ServiceError.no_cafe_floor_response()

        # 혼잡도 업데이트 금지시간 확인
        if not is_occupancy_update_possible():
            return ServiceError.update_forbidden_time_response()

        # 카페 오픈 유무 확인
        if not cafe_floor_object.cafe.is_opened:
            return ServiceError.cafe_closed_response()

        # 포인트 상세 로직
        now = datetime.datetime.now()
        midnight = datetime.datetime(year=now.year, month=now.month, day=now.day, hour=0, minute=0, second=1)
        today_this_cafe_update_logs = OccupancyRateUpdateLog.objects.filter(
            update__gte=midnight, cafe_floor__id=cafe_floor_id, user__id=request.user.id)

        # 회색 마커 이벤트 중인지 확인
        challenge_queryset = Challenge.objects.filter(name="회색마커추가포인트", available=False)
        if challenge_queryset.exists():
            challenge = challenge_queryset.first()
            now = datetime.datetime.now()
            if challenge.start <= now <= challenge.finish:
                log_queryset = OccupancyRateUpdateLog.objects.filter(
                    cafe_floor__id=cafe_floor_id, update__gte=now-datetime.timedelta(hours=RECENT_HOUR)
                )
                prediction_queryset = OccupancyRatePrediction.objects.filter(cafe_floor__id=cafe_floor_id)
                if not log_queryset.exists() and not prediction_queryset.exists():
                    serializer = ProfileSerializer(
                        request.user.profile,
                        data={"point": request.user.profile.point + challenge.goal},
                        partial=True
                    )
                    serializer.is_valid(raise_exception=True)
                    serializer.save()
                    FirebaseMessage.push_message(
                        title="📍 '회색마커를 찾아라!' 이벤트 보상 지급",
                        body=f"이벤트 기간({challenge.start.hour}시 ~ {challenge.finish.hour}시)중 혼잡도 업데이트로 {challenge.goal}P가 추가 지급되었습니다",
                        push_type=PushNotificationType.Activity.value,
                        user_object=request.user,
                        save_model=True
                    )

        # 지역 혼잡도 가져오기
        congestion = self.get_congestion(cafe_floor_object)

        if today_this_cafe_update_logs:
            # 오늘 이 카페에서 활동 이력 있음
            # 쿨타임 확인, 아직 안지났으면 에러
            recent_update_log = today_this_cafe_update_logs.order_by("-update")[0]
            if (now - recent_update_log.update).total_seconds() < UPDATE_COOLTIME * 60:
                return ServiceError.update_cooltime_response()

            # 오늘 이 카페에서 업데이트한 횟수 확인
            count_restriction = request.user.profile.grade.sharing_restriction_per_cafe
            if today_this_cafe_update_logs.count() >= count_restriction:
                saved_object = self.save_log(occupancy_rate=occupancy_rate, cafe_floor_id=cafe_floor_id,
                                             user_id=request.user.id, point=0, congestion=congestion)
                return Response(self.get_serializer(saved_object, read_only=True).data, status=status.HTTP_201_CREATED)

            # 오늘 이 카페에서 한 업데이트가 stack 초과한 업데이트인지 확인
            if not DailyActivityStack.objects.filter(update__gte=midnight, cafe_floor__id=cafe_floor_id,
                                                     user__id=request.user.id).exists():
                saved_object = self.save_log(occupancy_rate=occupancy_rate, cafe_floor_id=cafe_floor_id,
                                             user_id=request.user.id, point=0, congestion=congestion)
                return Response(self.get_serializer(saved_object, read_only=True).data, status=status.HTTP_201_CREATED)
        else:
            # 오늘 이 카페에서 활동 이력 없음
            stack_restriction = request.user.profile.grade.activity_stack_restriction_per_day
            today_other_cafe_stacks = DailyActivityStack.objects.filter(update__gte=midnight, user__id=request.user.id)
            if today_other_cafe_stacks.count() >= stack_restriction:
                # stack 초과(포인트 지급 불가)
                saved_object = self.save_log(occupancy_rate=occupancy_rate, cafe_floor_id=cafe_floor_id,
                                             user_id=request.user.id, point=0, congestion=congestion)
                return Response(self.get_serializer(saved_object, read_only=True).data, status=status.HTTP_201_CREATED)
            else:
                # stack 하나 쌓기
                stack_serializer = DailyActivityStackSerializer(
                    data={"user": request.user.id, "cafe_floor": cafe_floor_id})
                stack_serializer.is_valid(raise_exception=True)
                stack_serializer.save()

        # 데이터 많고 적음에 따라 포인트 다르게 책정
        point = PointCalculator.calculate_reward_based_on_data(cafe_floor_id)

        # occupancy_rate_update_log 작성
        saved_object = self.save_log(occupancy_rate=occupancy_rate, cafe_floor_id=cafe_floor_id,
                                     user_id=request.user.id, point=point, congestion=congestion)

        # 얻은 포인트 부여
        serializer = ProfileSerializer(request.user.profile, data={"point": request.user.profile.point + point}, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(self.get_serializer(saved_object, read_only=True).data,
                        status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        operation_id='내 활동 이력',
        operation_description='내 혼잡도 등록 활동 모두 보기',
        request_body=no_body,
        responses={200: OccupancyRateUpdateLogResponseSerializer(many=True)},
        manual_parameters=[AUTHORIZATION_MANUAL_PARAMETER]
    )
    def list(self, request, *args, **kwargs):
        queryset = self.queryset.filter(user__id=request.user.id).order_by("-update")
        return Response(data=self.get_serializer(queryset, many=True).data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_id='오늘 나의 업데이트',
        operation_description='내가 오늘 한 모든 혼잡도 업데이트 정보',
        responses={200: OccupancyRateUpdateLogResponseSerializer(many=True)},
        manual_parameters=[AUTHORIZATION_MANUAL_PARAMETER]
    )
    @action(methods=['get'], detail=False)
    def today_updated_log(self, request):
        now = datetime.datetime.now()
        today_updated_logs = self.queryset.filter(user__id=request.user.id, update__gt=datetime.datetime(
            year=now.year, month=now.month, day=now.day, hour=0, minute=0, second=1)).order_by("-update")
        return Response(data=self.get_serializer(today_updated_logs, many=True).data, status=status.HTTP_200_OK)


class LocationViewSet(
    mixins.ListModelMixin,
    GenericViewSet
):
    queryset = Location.objects.all()
    serializer_class = LocationResponseSerializer
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_id='지역 정보',
        operation_description='지도 깃발에 표시할 지역을 담은 정보',
        responses={200: LocationResponseSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return Response(data=self.get_serializer(self.queryset.filter(is_visible=True), many=True).data, status=status.HTTP_200_OK)


class CATIViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    GenericViewSet
):
    queryset = CATI.objects.all()
    serializer_class = CATISerializer

    def get_permissions(self):
        if self.action == 'list':
            return [AllowAny()]
        elif self.action == 'create':
            return [IsAuthenticated()]
        return []

    @swagger_auto_schema(
        operation_id='CATI정보',
        operation_description='query로 받은 cafe의 CATI 투표 정보를 모두 불러옴',
        responses={200: CATISerializer(many=True)},
        manual_parameters=[
            openapi.Parameter(
                name='cafe_id',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_NUMBER,
                required=True,
                description='조회를 원하는 카페 id',
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        cafe_id = self.request.query_params.get('cafe_id', None)
        if not cafe_id:
            return ServiceError.cati_cafe_id_missing_response()
        cafe_cati_queryset = self.queryset.filter(cafe__id=cafe_id)
        return Response(data=self.get_serializer(cafe_cati_queryset, many=True).data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_id='CATI투표',
        operation_description='해당 카페의 CATI를 투표함',
        request_body=SwaggerCATIRequestSerializer,
        responses={201: CATISerializer(many=True)},
        manual_parameters=[AUTHORIZATION_MANUAL_PARAMETER]
    )
    def create(self, request, *args, **kwargs):
        cafe_id = int(request.data.get("cafe_id"))
        openness = int(request.data.get("openness"))
        coffee = int(request.data.get("coffee"))
        workspace = int(request.data.get("workspace"))
        acidity = int(request.data.get("acidity"))
        try:
            cati_object = self.queryset.get(user__id=request.user.id, cafe__id=cafe_id)
            serializer = self.get_serializer(cati_object, partial=True, data={
                "openness": openness, "coffee": coffee, "workspace": workspace, "acidity": acidity
            })
        except CATI.DoesNotExist:
            serializer = self.get_serializer(data={
                "cafe": cafe_id,
                "user": request.user.id,
                "openness": openness,
                "coffee": coffee,
                "workspace": workspace,
                "acidity": acidity
            })
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)