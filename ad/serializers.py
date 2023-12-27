from rest_framework import serializers

from ad.models import AdLog


# 기본 serializer ------------------------------------------------------------
class AdLogSerializer(serializers.ModelSerializer):

    class Meta:
        model = AdLog
        fields = "__all__"

