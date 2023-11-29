from rest_framework import serializers

from utils import SwaggerSerializer


class SwaggerCafeAdditionRequestSerializer(SwaggerSerializer):
    cafe_name = serializers.CharField()
    dong_address = serializers.CharField()
    road_address = serializers.CharField()
    latitude = serializers.FloatField()
    longitude = serializers.FloatField()
    top_floor = serializers.IntegerField()
    bottom_floor = serializers.IntegerField()
    wall_socket_rate_list = serializers.ListField()
    opening_hour_list = serializers.ListField()
    etc = serializers.CharField()


class SwaggerWithdrawalRequestSerializer(SwaggerSerializer):
    reason = serializers.CharField()


class SwaggerUserMigrationRequestSerializer(SwaggerSerializer):
    phone_number = serializers.CharField(max_length=8)


