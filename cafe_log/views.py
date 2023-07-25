import datetime

from django.db.models import Count
from drf_yasg.utils import swagger_auto_schema, no_body
from rest_framework import status, mixins
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from cafe.models import Cafe
from cafe_log.models import CafeLog, CafeLogLike, CafeLogReport, Snapshot, CafeLogTheme
from cafe_log.serializers import CafeLogResponseSerializer, SnapShotSerializer, CafeLogLikeSerializer, \
    CafeLogReportSerializer, CafeLogSerializer
from cafe_log.swagger_serializers import SwaggerCafeLogListResponseSerializer, SwaggerCafeLogRequestSerializer, \
    SwaggerCafeLogReportRequestSerializer
from error import ServiceError
from notification.naver_sms import send_sms_to_admin
from utils import AUTHORIZATION_MANUAL_PARAMETER


class CafeLogPagination(PageNumberPagination):
    page_size = 20
    max_page_size = 10


class CafeLogViewSet(mixins.CreateModelMixin,
                   mixins.UpdateModelMixin,
                   mixins.DestroyModelMixin,
                   mixins.ListModelMixin,
                   GenericViewSet):
    queryset = CafeLog.objects.all()
    serializer_class = CafeLogResponseSerializer

    def get_permissions(self):
        if self.action == 'list' or self.action == 'retrieve' or self.action == 'hot_cafe_log':
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]

    @staticmethod
    def filter_private_logs(queryset):
        return queryset.filter(is_visible=True, is_private=False)

    @swagger_auto_schema(
        operation_id='최근 카페로그',
        operation_description='is_visible=True, is_private=False인 최근 카페로그들 반환',
        responses={200: SwaggerCafeLogListResponseSerializer()},
    )
    def list(self, request, *args, **kwargs):
        queryset = self.filter_private_logs(self.get_queryset())
        paginator = CafeLogPagination()
        page = paginator.paginate_queryset(queryset, self.request)
        serializer = self.get_serializer(page, many=True)
        return paginator.get_paginated_response(data=serializer.data)

    @swagger_auto_schema(
        method="get",
        operation_id='이번달 인기순 카페로그',
        operation_description='is_visible=True, is_private=False인 이번달 카페로그를 인기순으로 반환',
        responses={200: SwaggerCafeLogListResponseSerializer()},
    )
    @action(detail=False, methods=['get'])
    def hot_cafe_log(self, request):
        queryset = self.filter_private_logs(self.get_queryset())
        now = datetime.datetime.now()
        hot_logs = queryset.filter(
            created_at__gt=now - datetime.timedelta(days=30),
            is_visible=True, is_private=False
        ).annotate(like_count=Count('like')).order_by('-like_count')
        paginator = CafeLogPagination()
        page = paginator.paginate_queryset(hot_logs, request)
        serializer = self.get_serializer(page, many=True)
        return paginator.get_paginated_response(data=serializer.data)

    @swagger_auto_schema(
        method="get",
        operation_id='내 카페 로그',
        operation_description='내가 쓴 카페 로그들 반환',
        responses={200: SwaggerCafeLogListResponseSerializer()},
        manual_parameters=[AUTHORIZATION_MANUAL_PARAMETER]
    )
    @action(detail=False, methods=['get'])
    def my_cafe_log(self, request):
        my_logs = self.queryset.filter(id=request.user.id).order_by('-created_at')
        paginator = CafeLogPagination()
        page = paginator.paginate_queryset(my_logs, request)
        serializer = self.get_serializer(page, many=True)
        return paginator.get_paginated_response(data=serializer.data)

    @swagger_auto_schema(
        operation_id='카페 로그 작성',
        operation_description='카페 로그 작성, image에는 이미지 파일, image가 있으면 free테마 고정',
        request_body=SwaggerCafeLogRequestSerializer,
        responses={201: CafeLogResponseSerializer()},
        manual_parameters=[AUTHORIZATION_MANUAL_PARAMETER]
    )
    def create(self, request, *args, **kwargs):
        is_private = request.data.get("is_private")
        content = str(request.data.get("content"))
        cafe_id = int(request.data.get("cafe_id"))
        theme = str(request.data.get("theme"))
        snapshot_id = request.data.get("snapshot_id")

        if "image" in request.FILES:
            # 이미지 파일을 업로드했을 때
            image = request.FILES["image"]
            snapshot_serializer = SnapShotSerializer(data={"theme": theme, "image": image[0]})
            snapshot_serializer.is_valid(raise_exception=True)
            snapshot_id = snapshot_serializer.save().id
        else:
            snapshot_id = int(snapshot_id)

        try:
            Cafe.objects.get(id=cafe_id)
            Snapshot.objects.get(id=snapshot_id)
        except Cafe.DoesNotExist:
            return ServiceError.no_cafe_response()
        except Snapshot.DoesNotExist:
            return ServiceError.no_snapshot_response()

        serializer = CafeLogSerializer(data={
            "is_private": is_private,
            "theme": theme,
            "content": content,
            "cafe": cafe_id,
            "snapshot": snapshot_id,
            "user": request.user.id
        })
        serializer.is_valid(raise_exception=True)
        saved_object = serializer.save()
        return Response(self.get_serializer(saved_object, read_only=True).data, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        operation_id='카페 로그 수정',
        operation_description='작성했던 카페로그 수정, image에는 이미지 파일',
        request_body=SwaggerCafeLogRequestSerializer,
        responses={201: CafeLogResponseSerializer()},
        manual_parameters=[AUTHORIZATION_MANUAL_PARAMETER]
    )
    def update(self, request, *args, **kwargs):
        is_private = request.data.get("is_private")
        theme = request.data.get("theme")
        content = request.data.get("content")
        cafe_id = request.data.get("cafe_id")
        snapshot_id = request.data.get("snapshot_id")

        cafe_log_object = self.get_object()
        # 주인 여부 검사
        if cafe_log_object.user.id != request.user.id:
            return ServiceError.unauthorized_user_response()

        data = {}

        if is_private is not None:
            data["is_private"] = is_private
        if theme:
            data["theme"] = str(theme)
        if content:
            data["content"] = str(content)
        if cafe_id:
            data["cafe"] = int(cafe_id)
        if snapshot_id:
            data["snapshot"] = int(snapshot_id)
        if "image" in request.FILES:
            image = request.FILES["image"]
            # 기존에 free snapshot을 썼을 경우
            if cafe_log_object.snapshot.theme == CafeLogTheme.Free:
                snapshot_object = Snapshot.objects.get(snapshot__id=cafe_log_object.snapshot.id)
                snapshot_serializer = SnapShotSerializer(snapshot_object, data={"image": image[0]}, partial=True)
            # 기존에 default snapshot을 썼을 경우
            else:
                snapshot_serializer = SnapShotSerializer(data={"theme": CafeLogTheme.Free, "image": image[0]})
            snapshot_serializer.is_valid(raise_exception=True)
            data["snapshot"] = snapshot_serializer.save().id

        serializer = CafeLogSerializer(self.get_object(), data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        saved_object = serializer.save()
        return Response(self.get_serializer(saved_object, read_only=True).data, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        operation_id='카페 로그 삭제',
        operation_description='작성했던 카페로그 삭제',
        responses={204: ""},
        manual_parameters=[AUTHORIZATION_MANUAL_PARAMETER]
    )
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        # 요청 주인 여부 검사
        if instance.user.id != request.user.id:
            return ServiceError.unauthorized_user_response()

        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @swagger_auto_schema(
        method="put",
        operation_id='카페로그 좋아요',
        operation_description='해당 로그 좋아요 누르기',
        request_body=no_body,
        responses={201: CafeLogResponseSerializer()},
        manual_parameters=[AUTHORIZATION_MANUAL_PARAMETER]
    )
    @action(detail=True, methods=['put'])
    def like(self, request, pk):
        # 카페로그 유효성 검사
        try:
            self.queryset.get(id=pk)
        except CafeLog.DoesNotExist:
            return ServiceError.no_cafe_log_response()

        # 자추 검사
        cafe_log_object = self.get_object()
        if cafe_log_object.user.id == request.user.id:
            return ServiceError.like_to_my_log_forbidden_response()

        # 좋아요 눌렀는지 여부 검사
        try:
            CafeLogLike.objects.get(cafe_log__id=pk, user__id=request.user.id)
            return ServiceError.already_like_response()
        except CafeLogLike.DoesNotExist:
            pass

        serializer = CafeLogLikeSerializer(data={"cafe_log": pk, "user": request.user.id})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(self.get_serializer(self.get_object(), read_only=True).data, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        method="put",
        operation_id='카페로그 좋아요 취소',
        operation_description='해당 로그 좋아요 취소하기',
        request_body=no_body,
        responses={204: CafeLogResponseSerializer()},
        manual_parameters=[AUTHORIZATION_MANUAL_PARAMETER]
    )
    @action(detail=True, methods=['put'])
    def unlike(self, request, pk):
        # 카페로그 유효성 검사
        try:
            self.queryset.get(id=pk)
        except CafeLog.DoesNotExist:
            return ServiceError.no_cafe_log_response()

        cafe_log_object = self.get_object()

        # 좋아요 눌렸었는지 확인해서 있으면 삭제 없으면 에러
        try:
            CafeLogLike.objects.get(cafe_log__id=cafe_log_object.id, user__id=request.user.id).delete()
            return Response(data=self.get_serializer(cafe_log_object, read_only=True).data, status=status.HTTP_201_CREATED)
        except CafeLogLike.DoesNotExist:
            return ServiceError.no_cafe_log_like_response()

    @swagger_auto_schema(
        method="put",
        operation_id='카페로그 신고',
        operation_description='해당 로그 신고하기',
        request_body=SwaggerCafeLogReportRequestSerializer,
        responses={204: CafeLogResponseSerializer()},
        manual_parameters=[AUTHORIZATION_MANUAL_PARAMETER]
    )
    @action(detail=True, methods=['put'])
    def report(self, request, pk):
        reason = str(request.data.get("reason"))

        # 카페로그 유효성 검사
        try:
            self.queryset.get(id=pk)
        except CafeLog.DoesNotExist:
            return ServiceError.no_cafe_log_response()

        # 신고여부 검사
        try:
            CafeLogReport.objects.get(cafe_log__id=pk, user__id=request.user.id)
            return ServiceError.already_report_response()
        except CafeLogReport.DoesNotExist:
            pass

        serializer = CafeLogReportSerializer(data={"reason": reason, "cafe_log": pk, "user": request.user.id})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # 관리자에게 신고 알림
        send_sms_to_admin(
            content=f"카페 로그 신고 by {request.user.profile.nickname}\nhttp://localhost/admin/cafelogreport/")

        return Response(self.get_serializer(self.get_object(), read_only=True).data, status=status.HTTP_201_CREATED)
