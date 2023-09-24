from cafe.models import OccupancyRateUpdateLog
from cafejari.settings import OCCUPANCY_INSUFFICIENT_THRESHOLD, NO_DATA_POINT, OCCUPANCY_ENOUGH_THRESHOLD, \
    INSUFFICIENT_DATA_POINT, ENOUGH_DATA_POINT


class PointCalculator:

    @staticmethod
    def calculate_reward_based_on_data(cafe_floor_id):
        count = OccupancyRateUpdateLog.objects.filter(cafe_floor__id=cafe_floor_id, user__isnull=False).count()
        if count < OCCUPANCY_INSUFFICIENT_THRESHOLD:
            return NO_DATA_POINT
        elif count < OCCUPANCY_ENOUGH_THRESHOLD:
            return INSUFFICIENT_DATA_POINT
        else:
            return ENOUGH_DATA_POINT