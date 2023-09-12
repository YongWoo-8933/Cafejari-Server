from rest_framework import serializers

from utils import SwaggerSerializer


class SwaggerCafeAdditionRequestSerializer(SwaggerSerializer):
    cafe_name = serializers.CharField()
    dong_address = serializers.CharField()
    road_address = serializers.CharField()
    latitude = serializers.FloatField()
    longitude = serializers.FloatField()
    total_floor = serializers.IntegerField()
    first_floor = serializers.IntegerField()
    no_seat_floor_list = serializers.ListField()


class SwaggerWithdrawalRequestSerializer(SwaggerSerializer):
    reason = serializers.CharField()


class SwaggerUserMigrationRequestSerializer(SwaggerSerializer):
    phone_number = serializers.CharField(max_length=8)


