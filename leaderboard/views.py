from drf_yasg.utils import swagger_auto_schema, no_body
from rest_framework import mixins
from rest_framework.permissions import AllowAny
from rest_framework.viewsets import GenericViewSet

from leaderboard.models import TotalSharingRanker, WeekSharingRanker, MonthSharingRanker, MonthlyHotCafeLog
from leaderboard.serializers import TotalSharingRankerResponseSerializer, WeekSharingRankerResponseSerializer, \
    MonthSharingRankerResponseSerializer, MonthlyHotCafeLogResponseSerializer


class RankerViewSet(
    mixins.ListModelMixin,
    GenericViewSet
):
    permission_classes = [AllowAny]

    def filter_queryset(self, queryset):
        if len(queryset) > 100: queryset = queryset[:100]
        return queryset


class TotalSharingRankerViewSet(RankerViewSet):
    queryset = TotalSharingRanker.objects.all()
    serializer_class = TotalSharingRankerResponseSerializer

    @swagger_auto_schema(
        operation_id='누적 랭킹',
        operation_description='전 기간 누적 랭커, 최대 100명',
        request_body=no_body,
        responses={200: TotalSharingRankerResponseSerializer(many=True)},
    )
    def list(self, request, *args, **kwargs):
        return super(TotalSharingRankerViewSet, self).list(request, *args, **kwargs)


class MonthSharingRankerViewSet(RankerViewSet):
    queryset = MonthSharingRanker.objects.all()
    serializer_class = MonthSharingRankerResponseSerializer

    @swagger_auto_schema(
        operation_id='월간 랭킹',
        operation_description='이번달 랭커, 최대 100명',
        request_body=no_body,
        responses={200: MonthSharingRankerResponseSerializer(many=True)},
    )
    def list(self, request, *args, **kwargs):
        return super(MonthSharingRankerViewSet, self).list(request, *args, **kwargs)


class WeekSharingRankerViewSet(RankerViewSet):
    queryset = WeekSharingRanker.objects.all()
    serializer_class = WeekSharingRankerResponseSerializer

    @swagger_auto_schema(
        operation_id='주간 랭킹',
        operation_description='이번주 랭커, 최대 100명',
        request_body=no_body,
        responses={200: WeekSharingRankerResponseSerializer(many=True)},
    )
    def list(self, request, *args, **kwargs):
        return super(WeekSharingRankerViewSet, self).list(request, *args, **kwargs)


class MonthlyHotCafeLogViewSet(
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = MonthlyHotCafeLog.objects.all()
    serializer_class = MonthlyHotCafeLogResponseSerializer
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_id='이달의 카페 로그',
        operation_description='각 달에 선정된 카페 인기 로그들',
        request_body=no_body,
        responses={200: MonthlyHotCafeLogResponseSerializer(many=True)},
    )
    def list(self, request, *args, **kwargs):
        return super(MonthlyHotCafeLogViewSet, self).list(request, *args, **kwargs)
