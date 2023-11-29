from drf_yasg.utils import swagger_auto_schema
from rest_framework import mixins
from rest_framework.permissions import AllowAny
from rest_framework.viewsets import GenericViewSet

from app_config.models import Version
from app_config.serializers import VersionSerializer


class VersionViewSet(
    mixins.ListModelMixin,
    GenericViewSet
):
    queryset = Version.objects.all()
    serializer_class = VersionSerializer
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_id='버전정보',
        operation_description='앱 버전을 받아옴',
        responses={200: VersionSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super(VersionViewSet, self).list(request, *args, **kwargs)
