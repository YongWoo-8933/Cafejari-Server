from cafe.models import OccupancyRateUpdateLog, CafeVIP
from cafe.serializers import CafeVIPSerializer


def update_cafe_vip():
    occupancy_rate_update_log_queryset = OccupancyRateUpdateLog.objects.all()
    vip_dict = {}
    for occupancy_rate_update_log in occupancy_rate_update_log_queryset:
        if occupancy_rate_update_log.cafe_floor is None: continue
        if occupancy_rate_update_log.user is None: continue
        cafe_id = occupancy_rate_update_log.cafe_floor.cafe.id
        user_id = occupancy_rate_update_log.user.id
        # dict에 해당 카페가 추가되어 있음
        if cafe_id in vip_dict:
            # 유저의 해당 카페에서의 활동이 존재하면 카운트 +1
            if user_id in vip_dict[cafe_id]:
                vip_dict[cafe_id][user_id] = vip_dict[cafe_id][user_id] + 1
            # 유저의 해당 카페에서의 활동이 없으면 새로 만듦
            else:
                vip_dict[cafe_id][user_id] = 1
        # dict에 해당 카페가 추가되어 있지 않음
        else:
            vip_dict[cafe_id] = {user_id: 0}
    for cafe_id, user_dict in vip_dict.items():
        for user_id, count in user_dict.items():
            try:
                cafe_vip_object = CafeVIP.objects.get(cafe__id=cafe_id, user__id=user_id)
                serializer = CafeVIPSerializer(cafe_vip_object, data={"update_count": count}, partial=True)
            except CafeVIP.DoesNotExist:
                serializer = CafeVIPSerializer(data={"cafe": cafe_id, "user": user_id, "update_count": count})
            serializer.is_valid(raise_exception=True)
            serializer.save()






