from rest_framework import serializers

from user.serializers import UserResponseSerializer
from utils import SwaggerSerializer


# request
class SwaggerTokenRequestSerializer(SwaggerSerializer):
    refresh = serializers.CharField(max_length=255)


class SwaggerMakeNewProfileRequestSerializer(SwaggerSerializer):
    nickname = serializers.CharField(max_length=10, min_length=2)
    fcm_token = serializers.CharField(max_length=255)
    profile_image_id = serializers.IntegerField()
    marketing_push_enabled = serializers.BooleanField()


class SwaggerProfileUpdateRequestSerializer(SwaggerSerializer):
    nickname = serializers.CharField(max_length=10, min_length=2)
    gender = serializers.IntegerField()
    age_range = serializers.CharField(max_length=15)
    date_of_birth = serializers.CharField(max_length=4)
    phone_number = serializers.CharField(max_length=8)
    fcm_token = serializers.CharField(max_length=255)
    marketing_push_enabled = serializers.BooleanField()
    occupancy_push_enabled = serializers.BooleanField()
    log_push_enabled = serializers.BooleanField()
    profile_image_id = serializers.IntegerField()
    favorite_cafe_id_list = serializers.ListField()
    new_profile_image = serializers.CharField()
    cati_openness = serializers.IntegerField()
    cati_coffee = serializers.IntegerField()
    cati_workspace = serializers.IntegerField()
    cati_acidity = serializers.IntegerField()


class SwaggerKakaoLoginRequestSerializer(SwaggerSerializer):
    access_token = serializers.CharField(max_length=255)


class SwaggerAppleLoginRequestSerializer(SwaggerSerializer):
    id_token = serializers.CharField(max_length=255)
    code = serializers.CharField(max_length=255)



# response
class SwaggerSocialLoginFinishResponseSerializer(SwaggerSerializer):
    access = serializers.CharField(max_length=255)
    refresh = serializers.CharField(max_length=255)
    user = UserResponseSerializer()


class SwaggerKakaoCallbackResponseSerializer(SwaggerSerializer):
    user_exists = serializers.BooleanField()
    is_inactive = serializers.BooleanField()
    code = serializers.CharField(max_length=255)
    access_token = serializers.CharField(max_length=255)


class SwaggerAppleCallbackResponseSerializer(SwaggerSerializer):
    user_exists = serializers.BooleanField()
    is_inactive = serializers.BooleanField()
    code = serializers.CharField(max_length=255)
    id_token = serializers.CharField(max_length=255)


class SwaggerValidateNicknameResponseSerializer(SwaggerSerializer):
    nickname = serializers.CharField(max_length=10, min_length=2)


class SwaggerRefreshTokenResponseSerializer(SwaggerSerializer):
    access = serializers.CharField()
