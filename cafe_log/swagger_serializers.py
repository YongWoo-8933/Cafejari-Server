from rest_framework import serializers

from cafe_log.serializers import CafeLogResponseSerializer
from utils import SwaggerSerializer


# request serializer
class SwaggerCafeLogRequestSerializer(SwaggerSerializer):
    is_private = serializers.BooleanField()
    content = serializers.CharField()
    cafe_id = serializers.IntegerField()
    theme = serializers.CharField()
    snapshot_id = serializers.IntegerField()
    image = serializers.CharField()


class SwaggerCafeLogReportRequestSerializer(SwaggerSerializer):
    reason = serializers.CharField()


# response serializer
class SwaggerCafeLogListResponseSerializer(SwaggerSerializer):
    count = serializers.IntegerField()
    next = serializers.CharField()
    previous = serializers.CharField()
    results = CafeLogResponseSerializer(many=True)


