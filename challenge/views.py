import datetime

from drf_yasg.utils import swagger_auto_schema
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from challenge.models import Challenge, Challenger
from challenge.serializers import ChallengeResponseSerializer, ChallengerSerializer, ChallengerResponseSerializer
from challenge.swagger_serializers import SwaggerChallengeResponseSerializer, \
    SwaggerChallengeParticipateRequestSerializer
from error import ServiceError
from utils import AUTHORIZATION_MANUAL_PARAMETER


class ChallengeViewSet(
    mixins.ListModelMixin,
    GenericViewSet
):
    queryset = Challenge.objects.all()
    serializer_class = ChallengeResponseSerializer
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_id='챌린지 정보',
        operation_description='개최중인 챌린지 정보를 받음',
        responses={200: SwaggerChallengeResponseSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super(ChallengeViewSet, self).list(request, *args, **kwargs)

    @swagger_auto_schema(
        method="post",
        operation_id='챌린지 참가하기',
        operation_description='특정 챌린지에 챌린저로 등록',
        request_body=SwaggerChallengeParticipateRequestSerializer(),
        responses={201: SwaggerChallengeResponseSerializer()},
        manual_parameters=[AUTHORIZATION_MANUAL_PARAMETER],
    )
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def participate(self, queryset):
        challenge_id = int(self.request.data.get('challenge_id'))
        user_id = self.request.user.id

        selected_challenge_queryset = self.queryset.filter(id=challenge_id)

        if not selected_challenge_queryset.exists():
            return ServiceError.no_challenge_response()

        selected_challenge = selected_challenge_queryset[0]

        if not selected_challenge.available:
            return ServiceError.unavailable_challenge_response()

        if not selected_challenge.start < datetime.datetime.now() < selected_challenge.finish:
            return ServiceError.expired_challenge_response()

        if selected_challenge_queryset.filter(challenger__user__id=user_id).exists():
            return ServiceError.already_participate_response()

        if selected_challenge.participant_limit <= len(selected_challenge.challenger.all()):
            return ServiceError.participant_limit_exceed_response()

        serializer = ChallengerSerializer(data={"user": user_id, "challenge": selected_challenge.id})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(data=self.get_serializer(selected_challenge).data, status=status.HTTP_201_CREATED)


class ChallengerViewSet(
    mixins.ListModelMixin,
    GenericViewSet
):
    queryset = Challenger.objects.all()
    serializer_class = ChallengerResponseSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_id='참여중인 챌린지 정보',
        operation_description='내가 참여중인 챌린지 정보를 받음',
        responses={200: ChallengerResponseSerializer(many=True)},
        manual_parameters=[AUTHORIZATION_MANUAL_PARAMETER],
    )
    def list(self, request, *args, **kwargs):
        queryset = self.queryset.filter(user__id=request.user.id)
        return Response(data=self.get_serializer(queryset, many=True).data, status=status.HTTP_200_OK)