import datetime
import logging

from cafe.models import Cafe, OpeningHour
from cafe.serializers import CafeSerializer


def get_is_cafe_opened(open_at, close_at):
    now = datetime.datetime.now()
    if open_at is not None and close_at is not None:
        if open_at < close_at:
            return open_at <= now.time() <= close_at
        else:
            midnight_before = datetime.time(hour=23, minute=59, second=59)
            midnight_after = datetime.time(hour=0, minute=0, second=1)
            return open_at <= now.time() <= midnight_before or midnight_after <= now.time() <= close_at
    else:
        return True


def update_cafe_opening():
    try:
        now = datetime.datetime.now()
        for cafe_object in Cafe.objects.all():
            # 연결된 영업시간 정보가 있으면 진행
            try:
                if now.weekday() == 0:  # 월요일
                    is_opened = get_is_cafe_opened(cafe_object.opening_hour.mon_opening_time,
                                                   cafe_object.opening_hour.mon_closing_time)
                elif now.weekday() == 1:  # 화요일
                    is_opened = get_is_cafe_opened(cafe_object.opening_hour.tue_opening_time,
                                                   cafe_object.opening_hour.tue_closing_time)
                elif now.weekday() == 2:  # 수요일
                    is_opened = get_is_cafe_opened(cafe_object.opening_hour.wed_opening_time,
                                                   cafe_object.opening_hour.wed_closing_time)
                elif now.weekday() == 3:  # 목요일
                    is_opened = get_is_cafe_opened(cafe_object.opening_hour.thu_opening_time,
                                                   cafe_object.opening_hour.thu_closing_time)
                elif now.weekday() == 4:  # 금요일
                    is_opened = get_is_cafe_opened(cafe_object.opening_hour.fri_opening_time,
                                                   cafe_object.opening_hour.fri_closing_time)
                elif now.weekday() == 5:  # 토요일
                    is_opened = get_is_cafe_opened(cafe_object.opening_hour.sat_opening_time,
                                                   cafe_object.opening_hour.sat_closing_time)
                else:  # 일요일
                    is_opened = get_is_cafe_opened(cafe_object.opening_hour.sun_opening_time,
                                                   cafe_object.opening_hour.sun_closing_time)
                serializer = CafeSerializer(cafe_object, data={"is_opened": is_opened}, partial=True)
            # 연결된 영업시간 정보가 없으면 그냥 영업중으로 표시
            except OpeningHour.DoesNotExist:
                serializer = CafeSerializer(cafe_object, data={"is_opened": True}, partial=True)
            # 오픈 정보 저장
            serializer.is_valid(raise_exception=True)
            serializer.save()
    except Exception as e:
        logger = logging.getLogger('my')
        logger.error(e)