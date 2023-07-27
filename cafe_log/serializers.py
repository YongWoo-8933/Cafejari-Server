
from rest_framework import serializers

from cafe.serializers import CafeSerializer
from cafe_log.models import Snapshot, CafeLogLike, CafeLog, CafeLogReport
from user.serializers import PartialUserSerializer


# 기본 serializer ------------------------------------------------------------
from utils import ImageModelSerializer


class SnapShotSerializer(serializers.ModelSerializer):

    class Meta:
        model = Snapshot
        fields = "__all__"


class CafeLogLikeSerializer(serializers.ModelSerializer):

    class Meta:
        model = CafeLogLike
        fields = "__all__"


class CafeLogReportSerializer(serializers.ModelSerializer):

    class Meta:
        model = CafeLogReport
        fields = "__all__"


class CafeLogSerializer(serializers.ModelSerializer):

    class Meta:
        model = CafeLog
        fields = "__all__"



# 응용 serializer ------------------------------------------------------------
# 스냅샷 이미지 응답용 serializer
class SnapShotResponseSerializer(ImageModelSerializer):

    class Meta:
        model = Snapshot
        fields = "__all__"


# 카페 로그 응답 serializer
class CafeLogResponseSerializer(CafeLogSerializer):
    like = CafeLogLikeSerializer(read_only=True, many=True)
    report = CafeLogReportSerializer(read_only=True, many=True)
    user = PartialUserSerializer(read_only=True, many=True)
    cafe = CafeSerializer(read_only=True, many=True)
    snapshot = SnapShotResponseSerializer(read_only=True, many=True)

    def to_representation(self, instance):
        self.fields['user'] = PartialUserSerializer(read_only=True)
        self.fields['cafe'] = CafeSerializer(read_only=True)
        self.fields['snapshot'] = SnapShotResponseSerializer(read_only=True)
        return super(CafeLogResponseSerializer, self).to_representation(instance)