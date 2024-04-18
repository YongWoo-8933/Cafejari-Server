
import logging

from cafe.models import OccupancyRateUpdateLog
from challenge.models import Challenge
from challenge.serializers import ChallengePointSerializer, ChallengerSerializer
from user.serializers import ProfileSerializer


def check_occupancy_registration_challengers():
    try:
        challenges = Challenge.objects.filter(is_occupancy_registration_challenge=True, available=True)
        if not challenges.exists(): return
        for challenge in challenges:
            challengers = challenge.challenger.all()
            milestones = challenge.challenge_milestone.all()

            for challenger in challengers:
                challenger_points = challenger.challenge_point.all()
                update_count = OccupancyRateUpdateLog.objects.filter(
                    user__id=challenger.user.id,
                    update__range=(challenge.start, challenge.finish)
                ).count()
                progress_rate = round(update_count / float(challenge.goal), 2)
                if progress_rate > 1.0: progress_rate = 1.00
                serializer = ChallengerSerializer(challenger, data={"count": update_count, "progress_rate": progress_rate}, partial=True)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                for milestone in milestones:
                    if milestone.count == 0 or update_count < milestone.count: continue
                    if challenger_points.filter(point=milestone.point).exists(): continue
                    serializer = ChallengePointSerializer(data={
                        "point": milestone.point, "challenger": challenger.id, "description": f"혼잡도 등록 {milestone.count}회 달성"
                    })
                    serializer.is_valid(raise_exception=True)
                    serializer.save()
                    serializer = ProfileSerializer(challenger.user.profile, partial=True, data={"point": challenger.user.profile.point + milestone.point})
                    serializer.is_valid(raise_exception=True)
                    serializer.save()
    except Exception as e:
        logger = logging.getLogger('my')
        logger.error(e)