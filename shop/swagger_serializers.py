from rest_framework import serializers
from utils import SwaggerSerializer


class SwaggerGifticonRequestSerializer(SwaggerSerializer):
    item_id = serializers.IntegerField()


class SwaggerGifticonUpdateRequestSerializer(SwaggerSerializer):
    is_used = serializers.BooleanField()

