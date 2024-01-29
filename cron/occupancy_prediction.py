import datetime
import logging
import math
import random

import pytz
from django.db.models import Q, Count, ExpressionWrapper, F, Avg, TimeField

from cafe.models import OccupancyRateUpdateLog, CafeFloor, OccupancyRatePrediction, Congestion
from cafe.serializers import OccupancyRatePredictionSerializer
from cafejari.settings import UPDATE_POSSIBLE_TIME_FROM, UPDATE_POSSIBLE_TIME_TO, TIME_ZONE


def delete_occupancy_prediction(cafe_floor_id):
    try:
        prediction_object = OccupancyRatePrediction.objects.get(cafe_floor__id=cafe_floor_id)
        prediction_object.delete()
    except OccupancyRatePrediction.DoesNotExist:
        pass


def is_occupancy_update_possible():
    now = datetime.datetime.now()
    update_possible_time_from = datetime.time(UPDATE_POSSIBLE_TIME_FROM, 0, 0)
    update_possible_time_to = datetime.time(UPDATE_POSSIBLE_TIME_TO, 0, 0)
    return update_possible_time_from < now.time() < update_possible_time_to


def predict_occupancy():
    try:
        # 혼잡도 업데이트 가능시간인지 확인 하고, 불가능 시간이면 clear
        if not is_occupancy_update_possible():
            OccupancyRatePrediction.objects.all().delete()
            return
        # 혼잡도 로그가 하나라도 있는 + 해당 층에 자리가 있는 cafe floor만 불러옴
        filtered_cafe_floors = CafeFloor.objects.annotate(
            num_occupancy_updates=Count('occupancy_rate_update_log')
        ).filter(
            num_occupancy_updates__gte=1,
            has_seat=True
        )
        for cafe_floor_object in filtered_cafe_floors:
            # 카페가 열려 있는지 확인 하고, 닫혀 있다면 기존 예상 혼잡도 제거
            if not cafe_floor_object.cafe.is_opened:
                delete_occupancy_prediction(cafe_floor_object.id)
                continue
            # 현재 시각, 전후 80분 씩 설정, 평일 / 주말 구분
            now = datetime.datetime.now()
            start_datetime = now - datetime.timedelta(minutes=80)
            end_datetime = now + datetime.timedelta(minutes=80)
            start_time = datetime.time(start_datetime.hour, start_datetime.minute, 0)
            if end_datetime.hour == 0 or end_datetime.hour == 1:
                end_time = datetime.time(23, 59, 59)
            else:
                end_time = datetime.time(end_datetime.hour, end_datetime.minute, 0)
            if now.weekday() < 5:
                weekday_range = [2, 3, 4, 5, 6]
            else:
                weekday_range = [1, 7]
            # 평일/주말에 해당하는 전후 80분 내 로그 선 및 근접 시간순 정렬
            after_logs = OccupancyRateUpdateLog.objects.filter(
                Q(update__time__range=(now.time(), end_time)),
                update__week_day__in=weekday_range,
                cafe_floor__id=cafe_floor_object.id
            ).order_by('update__time')
            before_logs = OccupancyRateUpdateLog.objects.filter(
                Q(update__time__range=(start_time, now.time())),
                update__week_day__in=weekday_range,
                cafe_floor__id=cafe_floor_object.id
            ).order_by('-update__time')
            # 전, 후 로그 모두 존재하는 경우
            if after_logs.exists() and before_logs.exists():
                closest_future_log = after_logs.first()
                closest_past_log = before_logs.first()
                past_future_timedelta = closest_future_log.update - closest_past_log.update
                past_now_timedelta = now.replace(tzinfo=None) - closest_past_log.update
                x = past_now_timedelta.seconds
                x1 = past_future_timedelta.seconds
                y0 = closest_past_log.occupancy_rate
                y1 = closest_future_log.occupancy_rate
                # 혼잡도가 증가한 케이스
                if closest_future_log.occupancy_rate >= closest_past_log.occupancy_rate:
                    y_delta = math.pow(math.pow(y1 - y0, 2) * x / x1, 0.5)
                    average_occupancy_rate = float(y0) + y_delta
                # 혼잡도가 감소한 케이스
                else:
                    y_delta = math.pow(math.pow(y1 - y0, 2) * (x1 - x) / x1, 0.5)
                    average_occupancy_rate = float(y1) + y_delta
                # 가장 가까운 로그의 지역 혼잡도 산출
                if x < x1 / 2:
                    closest_congestion = closest_past_log.congestion
                else:
                    closest_congestion = closest_future_log.congestion
            # 후 로그만 있는 경우
            elif after_logs.exists():
                average_occupancy_rate = float(after_logs.first().occupancy_rate)
                closest_congestion = after_logs.first().congestion
            # 전 로그만 있는 경우
            elif before_logs.exists():
                average_occupancy_rate = float(before_logs.first().occupancy_rate)
                closest_congestion = before_logs.first().congestion
            # 전, 후 로그 모두 없는 경우 - 기존 예측 삭제
            else:
                delete_occupancy_prediction(cafe_floor_object.id)
                continue

            # 혼잡도 산출
            # 지역 혼잡도 factor 적용
            if cafe_floor_object.cafe.congestion_area and closest_congestion is not None:
                lookup_congestion_areas = cafe_floor_object.cafe.congestion_area.all()
                # 현재 해당 지역 혼잡도 index 설정
                current_congestion_index = 0
                for lookup_congestion_area in lookup_congestion_areas:
                    temp_congestion_index = list(Congestion).index(Congestion(lookup_congestion_area.current_congestion))
                    if current_congestion_index < temp_congestion_index:
                        current_congestion_index = temp_congestion_index
                # 현재 지역 혼잡도와 로그 지역 혼잡도 차이만큼 가감
                log_congestion_index = list(Congestion).index(Congestion(closest_congestion))
                congestion_index_diff = current_congestion_index - log_congestion_index
                average_occupancy_rate += 0.05 * congestion_index_diff
            # 랜덤 5% 적용
            average_occupancy_rate += random.uniform(-0.05, 0.05)
            # 음수 혼잡도, 1 이상 혼잡도 조정
            if average_occupancy_rate < 0:
                average_occupancy_rate = 0.0
            elif average_occupancy_rate > 1.0:
                average_occupancy_rate = 1.0
            # 예상 혼잡도 저장
            final_occupancy_rate = round(average_occupancy_rate, 2)
            try:
                prediction_object = OccupancyRatePrediction.objects.get(cafe_floor__id=cafe_floor_object.id)
                serializer = OccupancyRatePredictionSerializer(
                    prediction_object,
                    partial=True,
                    data={"occupancy_rate": final_occupancy_rate, "update": now}
                )
            except OccupancyRatePrediction.DoesNotExist:
                serializer = OccupancyRatePredictionSerializer(
                    data={"cafe_floor": cafe_floor_object.id, "occupancy_rate": final_occupancy_rate, "update": now}
                )
            serializer.is_valid(raise_exception=True)
            serializer.save()
    except Exception as e:
        logger = logging.getLogger('my')
        logger.error(e)


