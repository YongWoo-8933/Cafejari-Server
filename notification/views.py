from drf_yasg.utils import swagger_auto_schema, no_body
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from error import ServiceError
from notification.models import PushNotification
from notification.serializers import PushNotificationSerializer
from user.models import User
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
        instance = self.get_object()

        # 요청 주인 여부 검사
        try:
            instance.user.get(id=request.user.id)
        except User.DoesNotExist:
            return ServiceError.unauthorized_user_response()

        # user list에서 제외
        user_object_list = instance.user.exclude(id=request.user.id)
        if not user_object_list:
            self.perform_destroy(instance)
        else:
            user_id_list = [obj.id for obj in user_object_list]
            serializer = self.get_serializer(instance, data={"user": user_id_list}, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()

        return Response(status=status.HTTP_204_NO_CONTENT)
