from rest_framework import serializers

from cafe.serializers import CafeFloorCafeRepresentationSerializer, \
    CafeResponseSerializer, OccupancyRateUpdateLogCafeFloorRepresentationSerializer
from utils import SwaggerSerializer


# Request
class SwaggerOccupancyRegistrationRequestSerializer(SwaggerSerializer):
    occupancy_rate = serializers.DecimalField(max_digits=3, decimal_places=2)
    cafe_floor_id = serializers.IntegerField()


# Response
class SwaggerCafeFloorCafeRepresentationSerializer(CafeFloorCafeRepresentationSerializer):
    recent_user_updated_log = OccupancyRateUpdateLogCafeFloorRepresentationSerializer(many=True, read_only=True)
    recent_guest_updated_log = OccupancyRateUpdateLogCafeFloorRepresentationSerializer(many=True, read_only=True)


class SwaggerCafeResponseSerializer(CafeResponseSerializer):
    cafe_floor = SwaggerCafeFloorCafeRepresentationSerializer(read_only=True)


class SwaggerCafeSearchResponseSerializer(SwaggerSerializer):
    count = serializers.IntegerField()
    next = serializers.CharField()
    previous = serializers.CharField()
    results = SwaggerCafeResponseSerializer(many=True)
