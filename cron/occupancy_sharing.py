import datetime
import logging

from cafe.models import OccupancyRateUpdateLog
from cafe.serializers import OccupancyRateUpdateLogSerializer
from cafe.utils import PointCalculator
from notification.firebase_message import FirebaseMessage
from notification.models import PushNotificationType


def check_sharing_activity():
    try:
        now = datetime.datetime.now()
        before_10_minute = now - datetime.timedelta(minutes=10)
        before_20_minute = now - datetime.timedelta(minutes=20)
        between_10_20_logs = OccupancyRateUpdateLog.objects.filter(
            user__isnull=False,
            is_notified=False,
            cafe_floor__isnull=False,
            update__range=(before_20_minute, before_10_minute)
        )
        for log in between_10_20_logs:
            FirebaseMessage.push_message(
                title=f"아직 {log.cafe_floor.cafe.name}에 계신가요?",
                body=f"지금 혼잡도를 등록하면 {PointCalculator.calculate_reward_based_on_data(log.cafe_floor.id)}P 획득 가능!",
                push_type=PushNotificationType.Activity.value,
                user_object=log.user,
                save_model=True
            )
            serializer = OccupancyRateUpdateLogSerializer(log, data={"is_notified": True}, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
    except Exception as e:
        logger = logging.getLogger('my')
        logger.error(e)

