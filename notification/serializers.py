
from rest_framework import serializers
from notification.models import PushNotification, PopUpNotification
from utils import ImageModelSerializer


class PushNotificationSerializer(serializers.ModelSerializer):

    class Meta:
        model = PushNotification
        fields = "__all__"


class PopUpNotificationSerializer(serializers.ModelSerializer):

    class Meta:
        model = PopUpNotification
        fields = "__all__"



# 응용 serializer ------------------------------------------------------------
# 팝업 응답용 serializer
class PopUpNotificationResponseSerializer(ImageModelSerializer):

    class Meta:
        model = PopUpNotification
        fields = "__all__"

