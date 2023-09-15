from rest_framework import serializers

from cafe.serializers import CafeFloorCafeRepresentationSerializer, \
    CafeResponseSerializer, OccupancyRateUpdateLogCafeFloorRepresentationSerializer
from utils import SwaggerSerializer


# Request
class SwaggerOccupancyRegistrationRequestSerializer(SwaggerSerializer):
    occupancy_rate = serializers.DecimalField(max_digits=3, decimal_places=2)
    cafe_floor_id = serializers.IntegerField()

class SwaggerCATIRequestSerializer(SwaggerSerializer):
    cafe_id = serializers.IntegerField()
    openness = serializers.IntegerField()
    coffee = serializers.IntegerField()
    workspace = serializers.IntegerField()
    acidity = serializers.IntegerField()


# Response
class SwaggerCafeFloorCafeRepresentationSerializer(CafeFloorCafeRepresentationSerializer):
    recent_updated_log = OccupancyRateUpdateLogCafeFloorRepresentationSerializer(many=True, read_only=True)

class SwaggerCATIRepSerializer(SwaggerSerializer):
    openness = serializers.FloatField()
    coffee = serializers.FloatField()
    workspace = serializers.FloatField()
    acidity = serializers.FloatField()

class SwaggerCafeResponseSerializer(CafeResponseSerializer):
    cafe_floor = SwaggerCafeFloorCafeRepresentationSerializer(many=True, read_only=True)
    cati = SwaggerCATIRepSerializer(read_only=True)


# class SwaggerCafeSearchResponseSerializer(SwaggerSerializer):
#     count = serializers.IntegerField()
#     next = serializers.CharField()
#     previous = serializers.CharField()
#     results = SwaggerCafeResponseSerializer(many=True)
