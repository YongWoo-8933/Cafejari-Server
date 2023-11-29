import datetime

from django.db.models import Avg
from rest_framework import serializers
from cafe.models import District, Brand, CongestionArea, Cafe, OccupancyRatePrediction, CafeVIP, CafeImage, \
    OpeningHour, OccupancyRateUpdateLog, CafeFloor, DailyActivityStack, Location, CATI
from cafe.utils import PointCalculator
from cafejari.settings import RECENT_HOUR
from user.models import Grade, ProfileImage, Profile, User
from utils import ImageModelSerializer

# 기본 serializer ------------------------------------------------------------
class DistrictSerializer(serializers.ModelSerializer):

    class Meta:
        model = District
        fields = "__all__"


class LocationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Location
        fields = "__all__"


class CongestionAreaSerializer(serializers.ModelSerializer):

    class Meta:
        model = CongestionArea
        fields = "__all__"


class BrandSerializer(serializers.ModelSerializer):

    class Meta:
        model = Brand
        fields = "__all__"


class CATISerializer(serializers.ModelSerializer):

    class Meta:
        model = CATI
        fields = "__all__"


class CafeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Cafe
        fields = "__all__"


class CafeImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = CafeImage
        fields = "__all__"


class OpeningHourSerializer(serializers.ModelSerializer):

    class Meta:
        model = OpeningHour
        fields = "__all__"


class CafeFloorSerializer(serializers.ModelSerializer):

    class Meta:
        model = CafeFloor
        fields = "__all__"


class CafeVIPSerializer(serializers.ModelSerializer):

    class Meta:
        model = CafeVIP
        fields = "__all__"


class OccupancyRatePredictionSerializer(serializers.ModelSerializer):

    class Meta:
        model = OccupancyRatePrediction
        fields = "__all__"


class OccupancyRateUpdateLogSerializer(serializers.ModelSerializer):

    class Meta:
        model = OccupancyRateUpdateLog
        fields = "__all__"


class DailyActivityStackSerializer(serializers.ModelSerializer):

    class Meta:
        model = DailyActivityStack
        fields = "__all__"



# 응용 serializer ------------------------------------------------------------
# location image 응답용 serializer
class LocationResponseSerializer(ImageModelSerializer):

    class Meta:
        model = Location
        fields = "__all__"


# brand image 응답용 serializer
class BrandResponseSerializer(ImageModelSerializer):

    class Meta:
        model = Brand
        fields = "__all__"


# cafe image 응답용 serializer
class CafeImageResponseSerializer(ImageModelSerializer):

    class Meta:
        model = CafeImage
        fields = "__all__"


# partial user grade image 응답용 serializer
class PartialUserGradeResponseSerializer(ImageModelSerializer):

    class Meta:
        model = Grade
        fields = "__all__"


# partial user profile_image image 응답용 serializer
class PartialProfileImageResponseSerializer(ImageModelSerializer):

    class Meta:
        model = ProfileImage
        fields = "__all__"


# partial user profile_image image 응답용 serializer
class PartialProfileForRepSerializer(serializers.ModelSerializer):
    grade = PartialUserGradeResponseSerializer(read_only=True)
    profile_image = PartialProfileImageResponseSerializer(read_only=True)

    def to_representation(self, instance):
        self.fields['grade'] = PartialUserGradeResponseSerializer(read_only=True)
        self.fields['profile_image'] = PartialProfileImageResponseSerializer(read_only=True)
        return super(PartialProfileForRepSerializer, self).to_representation(instance)

    class Meta:
        model = Profile
        fields = ["id", "nickname", "grade", "profile_image"]


class PartialUserForRepSerializer(serializers.ModelSerializer):
    profile = PartialProfileForRepSerializer(read_only=True)

    class Meta:
        model = User
        fields = ["id", 'profile', 'date_joined']


# 맵 cafe 정보에 같이 실리는 vip 정보
class CafeVIPRepresentationSerializer(CafeVIPSerializer):
    user = PartialUserForRepSerializer(read_only=True)

    def to_representation(self, instance):
        self.fields['user'] = PartialUserForRepSerializer(read_only=True)
        return super(CafeVIPRepresentationSerializer, self).to_representation(instance)


# 맵 cafe 정보 속 cafe_floor안에 recent_log에 포함되는 업데이트 로그
class OccupancyRateUpdateLogCafeFloorRepresentationSerializer(OccupancyRateUpdateLogSerializer):
    user = PartialUserForRepSerializer(read_only=True)

    def to_representation(self, instance):
        self.fields['user'] = PartialUserForRepSerializer(read_only=True)
        return super(OccupancyRateUpdateLogCafeFloorRepresentationSerializer, self).to_representation(instance)


# 맵 cafe 정보 속 cafe_floor 참조 serializer
class CafeFloorCafeRepresentationSerializer(CafeFloorSerializer):
    recent_updated_log = serializers.SerializerMethodField(read_only=True)
    point_prediction = serializers.SerializerMethodField(read_only=True)
    occupancy_rate_prediction = OccupancyRatePredictionSerializer(read_only=True)

    @staticmethod
    def get_recent_updated_log(obj):
        # 카페 영업시간이 끝났으면 혼잡도 표시를 하지 않음
        if obj.cafe.is_opened:
            timedelta = datetime.timedelta(hours=RECENT_HOUR)
        else:
            timedelta = datetime.timedelta(milliseconds=1)
        filtered_logs = obj.occupancy_rate_update_log.filter(
            update__gte=(datetime.datetime.now() - timedelta)
        ).order_by("-update")
        serializer = OccupancyRateUpdateLogCafeFloorRepresentationSerializer(filtered_logs, many=True, read_only=True)
        return serializer.data

    @staticmethod
    def get_point_prediction(obj):
        return PointCalculator.calculate_reward_based_on_data(obj.id)


# 혼잡도 업데이트 로그 속 cafe_floor 참조 serializer
class CafeFloorLogRepresentationSerializer(CafeFloorSerializer):
    cafe = CafeSerializer(read_only=True)

    def to_representation(self, instance):
        self.fields['cafe'] = CafeSerializer(read_only=True)
        return super(CafeFloorLogRepresentationSerializer, self).to_representation(instance)


# 혼잡도 업데이트 로그의 생성, 나열 등에 표시할 serializer
class OccupancyRateUpdateLogResponseSerializer(OccupancyRateUpdateLogSerializer):
    cafe_floor = CafeFloorLogRepresentationSerializer(read_only=True)

    def to_representation(self, instance):
        self.fields['cafe_floor'] = CafeFloorLogRepresentationSerializer(read_only=True)
        return super(OccupancyRateUpdateLogResponseSerializer, self).to_representation(instance)


# 맵 검색에서 표시할 카페 정보
class CafeResponseSerializer(CafeSerializer):
    cafe_floor = CafeFloorCafeRepresentationSerializer(many=True, read_only=True)
    cafe_vip = CafeVIPRepresentationSerializer(many=True, read_only=True)
    cafe_image = serializers.SerializerMethodField(read_only=True)
    cati = serializers.SerializerMethodField(read_only=True, allow_null=True)
    opening_hour = OpeningHourSerializer(read_only=True)
    brand = BrandResponseSerializer(read_only=True)

    def to_representation(self, instance):
        self.fields['brand'] = BrandResponseSerializer(read_only=True)
        return super(CafeResponseSerializer, self).to_representation(instance)

    @staticmethod
    def get_cafe_image(obj):
        filtered_images = obj.cafe_image.filter(is_visible=True)
        serializer = CafeImageResponseSerializer(filtered_images, many=True, read_only=True)
        return serializer.data

    @staticmethod
    def get_cati(obj):
        filtered_cati_queryset = obj.cati.all()
        if filtered_cati_queryset.exists():
            openness_avg_dict = filtered_cati_queryset.aggregate(avg=Avg('openness'))
            coffee_avg_dict = filtered_cati_queryset.aggregate(avg=Avg('coffee'))
            workspace_avg_dict = filtered_cati_queryset.aggregate(avg=Avg('workspace'))
            acidity_avg_dict = filtered_cati_queryset.aggregate(avg=Avg('acidity'))
            return {
                "openness": openness_avg_dict["avg"],
                "coffee": coffee_avg_dict["avg"],
                "workspace": workspace_avg_dict["avg"],
                "acidity": acidity_avg_dict["avg"]
            }
        else:
            return None


# query 검색에서 표시할 카페 정보
class CafeSearchResponseSerializer(serializers.ModelSerializer):

    class Meta:
        model = Cafe
        fields = ["id", "name", "address", "latitude", "longitude"]

