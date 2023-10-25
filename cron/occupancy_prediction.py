import datetime
import logging
import random

from django.db.models import Q, Count, ExpressionWrapper, F, Avg, TimeField

from cafe.models import OccupancyRateUpdateLog, CafeFloor, OccupancyRatePrediction, Congestion
from cafe.serializers import OccupancyRatePredictionSerializer
from cafejari.settings import UPDATE_POSSIBLE_TIME_FROM, UPDATE_POSSIBLE_TIME_TO


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
        # 혼잡도 로그가 하나라도 있는 cafe floor만 불러옴
        filtered_cafe_floors = CafeFloor.objects.annotate(num_occupancy_updates=Count('occupancy_rate_update_log')).filter(num_occupancy_updates__gte=1)
        for cafe_floor_object in filtered_cafe_floors:
            # 카페가 열려 있는지 확인 하고, 닫혀 있다면 기존 예상 혼잡도 제거
            if not cafe_floor_object.cafe.is_opened:
                delete_occupancy_prediction(cafe_floor_object.id)
                continue
            # 현재 시각, 전후 한 시간씩 설정
            now = datetime.datetime.now()
            start_datetime = now - datetime.timedelta(hours=1)
            end_datetime = now + datetime.timedelta(hours=1)
            start_time = datetime.time(start_datetime.hour, start_datetime.minute, 0)
            end_time = datetime.time(end_datetime.hour, end_datetime.minute, 0)
            # 전후 한시간 내 로그 선별 및 근접 시간순 정렬
            between_logs = OccupancyRateUpdateLog.objects.filter(
                Q(update__time__range=(start_time, end_time)),
                cafe_floor__id=cafe_floor_object.id
            ).annotate(
                time_difference=ExpressionWrapper(
                    F('update__time') - now.time(),
                    output_field=TimeField()
                )
            ).order_by('-time_difference')[:3]
            # 로그가 있다면 혼잡도 산출
            if between_logs.exists():
                # 가까운 세개 로그 평균
                average_occupancy_rate = float(between_logs.aggregate(
                    average_occupancy_rate=Avg('occupancy_rate')
                )['average_occupancy_rate'])
                # 지역 혼잡도 factor 적용
                if cafe_floor_object.cafe.congestion_area:
                    lookup_congestion_areas = cafe_floor_object.cafe.congestion_area.all()
                    congestion_index = 0
                    for lookup_congestion_area in lookup_congestion_areas:
                        temp_congestion_index = list(Congestion).index(Congestion(lookup_congestion_area.current_congestion))
                        if congestion_index < temp_congestion_index:
                            congestion_index = temp_congestion_index
                    if average_occupancy_rate < 0.25:
                        occupancy_index = 0
                    elif average_occupancy_rate < 0.5:
                        occupancy_index = 1
                    elif average_occupancy_rate < 0.75:
                        occupancy_index = 2
                    else:
                        occupancy_index = 3
                    congestion_index_diff = congestion_index - occupancy_index
                    average_occupancy_rate += 0.05 * congestion_index_diff
                # 랜덤 5% 적용
                average_occupancy_rate += random.uniform(-0.05, 0.05)
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
            # 로그가 없다면 기존 예상 혼잡도 제거
            else:
                delete_occupancy_prediction(cafe_floor_object.id)
    except Exception as e:
        logger = logging.getLogger('my')
        logger.error(e)


