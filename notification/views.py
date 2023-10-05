from drf_yasg.utils import swagger_auto_schema, no_body
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from notification.models import PushNotification
from notification.serializers import PushNotificationSerializer
from utils import UserListDestroyViewSet, AUTHORIZATION_MANUAL_PARAMETER


class PushNotificationViewSet(UserListDestroyViewSet):
    queryset = PushNotification.objects.all()
    serializer_class = PushNotificationSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_id='내 알림',
        operation_description='내게 온 알림 리스트',
        request_body=no_body,
        responses={200: PushNotificationSerializer(many=True)},
        manual_parameters=[AUTHORIZATION_MANUAL_PARAMETER]
    )
    def list(self, request, *args, **kwargs):
        return super(PushNotificationViewSet, self).list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_id='내 알림 삭제',
        operation_description='내게 온 알림 삭제',
        request_body=no_body,
        responses={204: ""},
        manual_parameters=[AUTHORIZATION_MANUAL_PARAMETER]
    )
    def destroy(self, request, *args, **kwargs):
        return super(PushNotificationViewSet, self).destroy(request, *args, **kwargs)

    @swagger_auto_schema(
        method="UPDATE",
        operation_id='알림 확인',
        operation_description='알림 확인 업데이트',
        request_body=no_body,
        responses={201: PushNotificationSerializer()},
        manual_parameters=[AUTHORIZATION_MANUAL_PARAMETER]
    )
    @action(methods=['update'], detail=True)
    def read(self, request):
        notification_object = self.get_object()
        serializer = self.get_serializer(notification_object, data={"is_read": True}, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)
