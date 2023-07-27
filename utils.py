
import boto3
from django.contrib import admin
from django.utils.html import format_html
from drf_yasg import openapi
from rest_framework import mixins, status, serializers
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from cafejari.settings import AWS_STORAGE_BUCKET_NAME, AWS_S3_DOMAIN, BASE_IMAGE_URL, LOCAL
from error import ServiceError

# 유저가 자신의 모델만 받아오고, 삭제할 수 있는 viewset
class UserListDestroyViewSet(
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    GenericViewSet
):

    def list(self, request, *args, **kwargs):
        queryset = self.queryset.filter(user__id=request.user.id)
        return Response(data=self.get_serializer(queryset, many=True).data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        # 요청 주인 여부 검사
        if instance.user.id != request.user.id:
            return ServiceError.unauthorized_user_response()

        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


# swagger용 serializer
class SwaggerSerializer(serializers.Serializer):

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass


# swagger 요청중 인증 필요를 알리는 부분
AUTHORIZATION_MANUAL_PARAMETER = openapi.Parameter(
    name='Authorization',
    in_=openapi.IN_HEADER,
    type=openapi.TYPE_STRING,
    required=True,
    description='Bearer {access_token} 필요',
)


# s3 이미지 업로드 관련
class S3ImageManager:
    _client = None

    def __new__(cls):
        if cls._client is None:
            cls._client = boto3.client('s3')
        return cls._client

    def upload_image(self, file, path):
        self._client.upload_fileobj(file, AWS_STORAGE_BUCKET_NAME, path)

    def delete_image(self, path):
        self._client.delete_object(Bucket=AWS_STORAGE_BUCKET_NAME, Key=path)


# 이미지 파일을 가지고 있는 모델의 admin
class ImageModelAdmin(admin.ModelAdmin):

    def delete_model(self, request, obj):
        s3_manager = S3ImageManager()
        s3_manager.delete_image(path=obj.image)
        obj.delete()

    def delete_queryset(self, request, queryset):
        s3_manager = S3ImageManager()
        for obj in queryset:
            s3_manager.delete_image(path=obj.image)
            obj.delete()


# 이미지 파일을 가지고 있는 모델의 serializer
class ImageModelSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    @staticmethod
    def get_image(obj):
        return replace_image_domain(url=obj.image.url)


# s3 도메인을 image 도메인으로 교체
def replace_image_domain(url):
    return str(url).replace(AWS_S3_DOMAIN, BASE_IMAGE_URL) if not LOCAL else url