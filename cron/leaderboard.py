import datetime
import logging
from collections import defaultdict

from pytz import timezone

from cafe.models import OccupancyRateUpdateLog
from leaderboard.models import WeekSharingRanker, MonthSharingRanker, TotalSharingRanker
from leaderboard.serializers import TotalSharingRankerSerializer, MonthSharingRankerSerializer, \
    WeekSharingRankerSerializer


def update_leaders():
    try:
        # ranker clear
        WeekSharingRanker.objects.all().delete()
        MonthSharingRanker.objects.all().delete()
        TotalSharingRanker.objects.all().delete()
        # datetime 세팅
        now = datetime.datetime.now(timezone('Asia/Seoul'))
        first_datetime_midnight_of_this_month = datetime.datetime(
            year=now.year, month=now.month, day=1, hour=0, minute=0, second=1, tzinfo=timezone('Asia/Seoul')
        )
        first_datetime_of_this_week = now - datetime.timedelta(days=now.weekday())
        first_datetime_midnight_of_this_week = datetime.datetime(
            year=first_datetime_of_this_week.year, month=first_datetime_of_this_week.month,
            day=first_datetime_of_this_week.day, hour=0, minute=0, second=1, tzinfo=timezone('Asia/Seoul')
        )
        # total, month, week queryset 세팅
        occupancy_rate_update_log_queryset = OccupancyRateUpdateLog.objects.filter(
            user__isnull=False, cafe_floor__isnull=False
        )
        this_month_occupancy_rate_update_log_queryset = occupancy_rate_update_log_queryset.filter(
            update__gt=first_datetime_midnight_of_this_month
        )
        this_week_occupancy_rate_update_log_queryset = this_month_occupancy_rate_update_log_queryset.filter(
            update__gt=first_datetime_midnight_of_this_week
        )
        # 랭커 dict 정리
        total_ranker_dict = defaultdict(lambda: 0)
        month_ranker_dict = defaultdict(lambda: 0)
        week_ranker_dict = defaultdict(lambda: 0)
        for log in occupancy_rate_update_log_queryset:
            total_ranker_dict[log.user.id] += 1
        for log in this_month_occupancy_rate_update_log_queryset:
            month_ranker_dict[log.user.id] += 1
        for log in this_week_occupancy_rate_update_log_queryset:
            week_ranker_dict[log.user.id] += 1
        # 랭커 serializer 저장
        for user_id, count in total_ranker_dict.items():
            try:
                user = TotalSharingRanker.objects.get(user__id=user_id)
                serializer = TotalSharingRankerSerializer(user, data={"sharing_count": count}, partial=True)
            except TotalSharingRanker.DoesNotExist:
                serializer = TotalSharingRankerSerializer(data={"user": user_id, "sharing_count": count})
            serializer.is_valid(raise_exception=True)
            serializer.save()
        for user_id, count in month_ranker_dict.items():
            serializer = MonthSharingRankerSerializer(data={"user": user_id, "sharing_count": count})
            serializer.is_valid(raise_exception=True)
            serializer.save()
        for user_id, count in week_ranker_dict.items():
            serializer = WeekSharingRankerSerializer(data={"user": user_id, "sharing_count": count})
            serializer.is_valid(raise_exception=True)
            serializer.save()
    except Exception as e:
        logger = logging.getLogger('my')
        logger.error(e)
