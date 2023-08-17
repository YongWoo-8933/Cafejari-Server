from datetime import datetime, timedelta
from rest_framework import serializers
from cafe.models import District, Brand, CongestionArea, Cafe, OccupancyRatePrediction, CafeVIP, CafeImage, \
    OpeningHour, OccupancyRateUpdateLog, CafeFloor, CafeTypeTag, DailyActivityStack
from cafejari.settings import RECENT_HOUR
from user.serializers import PartialUserSerializer
from utils import ImageModelSerializer

# 기본 serializer ------------------------------------------------------------
class DistrictSerializer(serializers.ModelSerializer):

    class Meta:
        model = District
        fields = "__all__"


class CongestionAreaSerializer(serializers.ModelSerializer):

    class Meta:
        model = CongestionArea
        fields = "__all__"


class BrandSerializer(serializers.ModelSerializer):

    class Meta:
        model = Brand
        fields = "__all__"


class CafeTypeTagSerializer(serializers.ModelSerializer):

    class Meta:
        model = CafeTypeTag
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


# 맵 cafe 정보에 같이 실리는 vip 정보
class CafeVIPRepresentationSerializer(CafeVIPSerializer):
    user = PartialUserSerializer(read_only=True)

    def to_representation(self, instance):
        self.fields['user'] = PartialUserSerializer(read_only=True)
        return super(CafeVIPRepresentationSerializer, self).to_representation(instance)


# 맵 cafe 정보 속 cafe_floor안에 recent_log에 포함되는 업데이트 로그
class OccupancyRateUpdateLogCafeFloorRepresentationSerializer(OccupancyRateUpdateLogSerializer):
    user = PartialUserSerializer(read_only=True)

    def to_representation(self, instance):
        self.fields['user'] = PartialUserSerializer(read_only=True)
        return super(OccupancyRateUpdateLogCafeFloorRepresentationSerializer, self).to_representation(instance)


# 맵 cafe 정보 속 cafe_floor 참조 serializer
class CafeFloorCafeRepresentationSerializer(CafeFloorSerializer):
    recent_updated_log = serializers.SerializerMethodField(read_only=True)
    occupancy_rate_prediction = OccupancyRatePredictionSerializer(read_only=True)

    @staticmethod
    def get_recent_updated_log(obj):
        filtered_logs = obj.occupancy_rate_update_log.filter(
            update__gte=(datetime.now() - timedelta(hours=RECENT_HOUR))
        )
        serializer = OccupancyRateUpdateLogCafeFloorRepresentationSerializer(filtered_logs, many=True, read_only=True)
        return serializer.data


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


# query 검색에서 표시할 카페 정보
class CafeSearchResponseSerializer(serializers.ModelSerializer):

    class Meta:
        model = Cafe
        fields = ["id", "name", "address"]

