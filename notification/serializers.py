
from rest_framework import serializers
from notification.models import PushNotification


class PushNotificationSerializer(serializers.ModelSerializer):

    class Meta:
        model = PushNotification
        fields = "__all__"

