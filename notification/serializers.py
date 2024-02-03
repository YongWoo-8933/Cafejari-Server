
from rest_framework import serializers
from notification.models import PushNotification, PopUpNotification


class PushNotificationSerializer(serializers.ModelSerializer):

    class Meta:
        model = PushNotification
        fields = "__all__"

class PopUpNotificationSerializer(serializers.ModelSerializer):

    class Meta:
        model = PopUpNotification
        fields = "__all__"

