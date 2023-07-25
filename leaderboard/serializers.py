
from rest_framework import serializers
from cafe_log.serializers import CafeLogResponseSerializer
from leaderboard.models import TotalSharingRanker, MonthSharingRanker, WeekSharingRanker, MonthlyHotCafeLog
from user.serializers import PartialUserSerializer


# 기본 serializer ---------------------------------------------------------------------------------------
class TotalSharingRankerSerializer(serializers.ModelSerializer):

    class Meta:
        model = TotalSharingRanker
        fields = "__all__"


class MonthSharingRankerSerializer(serializers.ModelSerializer):

    class Meta:
        model = MonthSharingRanker
        fields = "__all__"


class WeekSharingRankerSerializer(serializers.ModelSerializer):

    class Meta:
        model = WeekSharingRanker
        fields = "__all__"


class MonthlyHotCafeLogSerializer(serializers.ModelSerializer):

    class Meta:
        model = MonthlyHotCafeLog
        fields = "__all__"



# 응용 serializer ---------------------------------------------------------------------------------------
class TotalSharingRankerResponseSerializer(TotalSharingRankerSerializer):
    user = PartialUserSerializer(read_only=True)

    def to_representation(self, instance):
        self.fields['user'] = PartialUserSerializer(read_only=True)
        return super(TotalSharingRankerResponseSerializer, self).to_representation(instance)


class MonthSharingRankerResponseSerializer(MonthSharingRankerSerializer):
    user = PartialUserSerializer(read_only=True)

    def to_representation(self, instance):
        self.fields['user'] = PartialUserSerializer(read_only=True)
        return super(MonthSharingRankerResponseSerializer, self).to_representation(instance)


class WeekSharingRankerResponseSerializer(WeekSharingRankerSerializer):
    user = PartialUserSerializer(read_only=True)

    def to_representation(self, instance):
        self.fields['user'] = PartialUserSerializer(read_only=True)
        return super(WeekSharingRankerResponseSerializer, self).to_representation(instance)


class MonthlyHotCafeLogResponseSerializer(MonthlyHotCafeLogSerializer):

    def to_representation(self, instance):
        self.fields['cafe_log'] = CafeLogResponseSerializer(read_only=True)
        return super(MonthlyHotCafeLogResponseSerializer, self).to_representation(instance)