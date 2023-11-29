
from rest_framework import serializers
from app_config.models import Version


# 기본 serializer ------------------------------------------------------------
class VersionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Version
        fields = "__all__"


