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


class SwaggerCafeInformationSuggestionRequestSerializer(SwaggerSerializer):
    cafe_id = serializers.IntegerField()
    is_closed = serializers.BooleanField()
    top_floor = serializers.IntegerField()
    bottom_floor = serializers.IntegerField()
    opening_hour_list = serializers.ListField()
    wall_socket_rate_list = serializers.ListField()
    restroom_list = serializers.ListField()
    no_seat_list = serializers.ListField()
    latitude = serializers.FloatField()
    longitude = serializers.FloatField()
    etc = serializers.CharField()


class SwaggerWithdrawalRequestSerializer(SwaggerSerializer):
    reason = serializers.CharField()


class SwaggerUserMigrationRequestSerializer(SwaggerSerializer):
    phone_number = serializers.CharField(max_length=8)


class SwaggerAppFeedbackRequestSerializer(SwaggerSerializer):
    reason = serializers.CharField()


