import random
import re
import time

import requests
from allauth.socialaccount.models import SocialAccount
from allauth.socialaccount.providers.kakao.views import KakaoOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.jwt_auth import unset_jwt_cookies
from dj_rest_auth.registration.views import SocialLoginView
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import redirect
from drf_yasg import openapi
from rest_framework import mixins, status
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt.views import TokenRefreshView

from cafejari import settings
from cafejari.settings import KAKAO_REST_API_KEY, KAKAO_REDIRECT_URL, DEBUG
from error import ServiceError
from notification.naver_sms import send_sms_to_admin
from user.models import User, Profile, Grade, NicknameAdjective, NicknameNoun, ProfileImage
from user.swagger_serializers import SwaggerMakeNewProfileRequestSerializer, \
    SwaggerProfileUpdateRequestSerializer, SwaggerKakaoCallbackResponseSerializer, \
    SwaggerKakaoLoginFinishResponseSerializer, SwaggerTokenRequestSerializer, \
    SwaggerValidateNicknameResponseSerializer, SwaggerKakaoLoginRequestSerializer, SwaggerRefreshTokenResponseSerializer
from user.serializers import ProfileResponseSerializer, UserResponseSerializer, ProfileSerializer, \
    ProfileImageSerializer, GradeResponseSerializer, ProfileImageResponseSerializer
from drf_yasg.utils import swagger_auto_schema, no_body

from utils import AUTHORIZATION_MANUAL_PARAMETER
from rest_framework_simplejwt.tokens import RefreshToken


class GradeViewSet(
    mixins.ListModelMixin,
    GenericViewSet
):
    queryset = Grade.objects.all()
    serializer_class = GradeResponseSerializer
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_id='grade 종류 받아오기',
        operation_description='존배하는 모든 grade 종류 반환',
        responses={200: GradeResponseSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super(GradeViewSet, self).list(request, *args, **kwargs)


class UserViewSet(GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserResponseSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        method='get',
        operation_id='유저정보 받아오기',
        operation_description='access_token에서 유저 정보를 받아 반환',
        manual_parameters=[AUTHORIZATION_MANUAL_PARAMETER]
    )
    @action(methods=['get'], detail=False)
    def user(self, queryset):
        return Response(data=self.get_serializer(self.request.user, read_only=True).data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        method='post',
        operation_id='로그아웃',
        operation_description='refresh token을 받고 해당 유저를 logout시킴',
        request_body=SwaggerTokenRequestSerializer,
        responses={200: ""},
        manual_parameters=[AUTHORIZATION_MANUAL_PARAMETER]
    )
    @action(methods=['post'], detail=False)
    def logout(self, request):
        try:
            request.user.auth_token.delete()
        except (AttributeError, ObjectDoesNotExist):
            pass

        response = Response(status=status.HTTP_200_OK)
        unset_jwt_cookies(response)

        token = RefreshToken(request.data['refresh'])
        token.blacklist()
        return response

    @swagger_auto_schema(
        method='post',
        operation_id='프로필 만들기',
        operation_description='유저의 social 정보를 바탕으로 프로필 제작',
        request_body=SwaggerMakeNewProfileRequestSerializer,
        responses={201: UserResponseSerializer()},
        manual_parameters=[AUTHORIZATION_MANUAL_PARAMETER]
    )
    @action(methods=['post'], detail=True)
    def make_new_profile(self, queryset, pk):
        user_object = self.request.user
        nickname = self.request.data.get('nickname')
        fcm_token = self.request.data.get('fcm_token')
        profile_image_id = self.request.data.get('profile_image_id')
        try:
            _ = user_object.profile
            return ServiceError.profile_exist_response()
        except ObjectDoesNotExist:
            social_account_object = user_object.socialaccount_set.first()
            if not social_account_object:
                return ServiceError.no_social_account_response()
            grade_object = Grade.objects.first()
            profile_data = {"nickname": nickname, "grade": grade_object.id, "user": user_object.id}
            if fcm_token:
                profile_data["fcm_token"] = fcm_token
            if profile_image_id:
                profile_data["profile_image"] = int(profile_image_id)
            if social_account_object.provider == "kakao":
                extra_json_data = social_account_object.extra_data.get("kakao_account")
                age_range = extra_json_data.get("age_range")
                birthday = extra_json_data.get("birthday")
                gender = extra_json_data.get("gender")
                phone_number = extra_json_data.get("phone_number")
                if age_range:
                    profile_data["age_range"] = age_range
                if birthday:
                    profile_data["date_of_birth"] = birthday
                if gender:
                    profile_data["gender"] = 0 if gender == "male" else 1
                if phone_number:
                    profile_data["phone_number"] = phone_number.replace("-", "").replace("+82 ", "")

            profile_serializer = ProfileSerializer(data=profile_data)
            profile_serializer.is_valid(raise_exception=True)
            profile_serializer.save()

            time.sleep(0.1)

            return Response(data=self.get_serializer(self.request.user, read_only=True).data, status=status.HTTP_201_CREATED)


class ProfileViewSet(
    mixins.UpdateModelMixin,
    GenericViewSet
):
    queryset = Profile.objects.all()
    serializer_class = ProfileResponseSerializer
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        method='get',
        operation_id='닉네임 검사',
        operation_description='닉네임 설정 전 닉네임이 유효한지 확인',
        responses={200: SwaggerValidateNicknameResponseSerializer()},
        manual_parameters=[
            openapi.Parameter(
                name='nickname',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                required=True,
                description='검사하려는 닉네임 전송',
            )
        ]
    )
    @action(methods=['get'], detail=False)
    def validate_nickname(self, queryset):
        nickname = self.request.query_params.get('nickname')
        changed_nickname = re.sub('[^a-zA-Z가-힣0-9]', '', nickname).strip()
        changed_nickname = changed_nickname.replace(" ", "")
        if nickname != changed_nickname:
            return ServiceError.invalid_nickname_response()
        elif not 2 <= len(nickname) <= 10:
            return ServiceError.invalid_nickname_length_response()
        else:
            try:
                Profile.objects.get(nickname=changed_nickname)
                return ServiceError.duplicated_nickname_response()
            except Profile.DoesNotExist:
                return Response({'nickname': nickname}, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        method='get',
        operation_id='닉네임 자동 생성',
        operation_description='자동으로 생성된 닉네임 반환',
        request_body=no_body,
        responses={200: SwaggerValidateNicknameResponseSerializer()}
    )
    @action(methods=['get'], detail=False)
    def auto_generate_nickname(self, queryset):
        adjectives = [obj.value for obj in NicknameAdjective.objects.all()]
        nouns = [obj.value for obj in NicknameNoun.objects.all()]
        stack = 0
        if adjectives and nouns:
            while True:
                stack += 1
                nickname = random.choice(adjectives) + random.choice(nouns)
                try:
                    _ = Profile.objects.get(nickname=nickname)
                    if stack > 50:
                        break
                    else:
                        continue
                except Profile.DoesNotExist:
                    break
            if stack > 50:
                send_sms_to_admin(content="닉네임 자동 생성 스택이 50회가 넘었습니다. 경우의 수를 늘려주세요")
                return Response(data={"nickname": ""}, status=status.HTTP_200_OK)
            else:
                return Response(data={"nickname": nickname}, status=status.HTTP_200_OK)
        send_sms_to_admin(content="형용사나 명사가 없어 닉네임 자동생성에 실패했습니다")
        return Response(data={"nickname": ""}, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_id='프로필 업데이트',
        operation_description='프로필 정보를 받아 수정하기, new_profile_image에는 이미지 파일',
        request_body=SwaggerProfileUpdateRequestSerializer,
        responses={201: UserResponseSerializer()},
        manual_parameters=[AUTHORIZATION_MANUAL_PARAMETER]
    )
    def update(self, request, *args, **kwargs):
        # 유저 권한 확인
        profile_object = self.get_object()
        if profile_object.user.id != request.user.id:
            return ServiceError.unauthorized_user_response()

        nickname = request.data.get("nickname")
        gender = request.data.get("gender")
        age_range = request.data.get("age_range")
        date_of_birth = request.data.get("date_of_birth")
        phone_number = request.data.get("phone_number")
        marketing_push_enabled = request.data.get("marketing_push_enabled")
        occupancy_push_enabled = request.data.get("occupancy_push_enabled")
        log_push_enabled = request.data.get("log_push_enabled")
        profile_image_id = request.data.get("profile_image_id")
        favorite_cafe_id_list = request.data.get("favorite_cafe_id_list")
        new_profile_image = request.FILES["new_profile_image"] if "new_profile_image" in request.FILES else None

        data = {}

        if nickname is not None:
            data["nickname"] = str(nickname)
        if gender is not None:
            data["gender"] = int(gender)
        if age_range is not None:
            data["age_range"] = str(age_range)
        if date_of_birth is not None:
            data["date_of_birth"] = str(date_of_birth)
        if phone_number is not None:
            data["phone_number"] = str(phone_number)
        if marketing_push_enabled is not None:
            data["marketing_push_enabled"] = marketing_push_enabled
        if occupancy_push_enabled is not None:
            data["occupancy_push_enabled"] = occupancy_push_enabled
        if log_push_enabled is not None:
            data["log_push_enabled"] = log_push_enabled
        if profile_image_id is not None:
            data["profile_image"] = int(profile_image_id)
        if favorite_cafe_id_list:
            favorite_cafe_data = [int(cafe_id) for cafe_id in favorite_cafe_id_list]
            data["favorite_cafe"] = favorite_cafe_data
        if new_profile_image is not None:
            profile_image_serializer = ProfileImageSerializer(data={"is_default": False, "image": new_profile_image[0]})
            profile_image_serializer.is_valid(raise_exception=True)
            data["profile_image"] = profile_image_serializer.save().id

        serializer = ProfileSerializer(profile_object, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        time.sleep(0.1)
        return Response(UserResponseSerializer(request.user, read_only=True).data, status=status.HTTP_201_CREATED)


class ProfileImageViewSet(
    mixins.ListModelMixin,
    GenericViewSet
):
    queryset = ProfileImage.objects.all()
    serializer_class = ProfileImageSerializer
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_id='프로필 이미지',
        operation_description='존재하는 모든 default profile image를 반환',
        request_body=no_body,
        responses={200: ProfileImageResponseSerializer(many=True)},
    )
    def list(self, request, *args, **kwargs):
        self.queryset.filter(is_default=True)
        serializer = ProfileImageResponseSerializer(self.queryset.filter(is_default=True), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CustomTokenRefreshView(TokenRefreshView):

    @swagger_auto_schema(
        operation_id='토큰 재발급',
        operation_description='refresh 토큰을 통해 새로운 access 토큰 발급',
        request_body=SwaggerTokenRequestSerializer,
        responses={200: SwaggerRefreshTokenResponseSerializer()}
    )
    def post(self, request, *args, **kwargs):
        return super(CustomTokenRefreshView, self).post(request, *args, **kwargs)


rest_api_key = getattr(settings, 'KAKAO_REST_API_KEY')
redirect_url = getattr(settings, 'KAKAO_REDIRECT_URL')


@swagger_auto_schema(
    method='get',
    operation_id='디버그 서버 code 발급용 view',
    operation_description='디버그 모드에서 카카오 서버 code를 발급받기위한 로직',
    request_body=no_body
)
@api_view(['GET'])
@permission_classes((AllowAny,))
def kakao_login(request):
    if DEBUG:
        return redirect(
            f"https://kauth.kakao.com/oauth/authorize?client_id={rest_api_key}&redirect_uri={redirect_url}&response_type=code"
        )
    else:
        return ServiceError.is_not_debug_mode_response()


@swagger_auto_schema(
    method='post',
    operation_id='카카오 로그인',
    operation_description="카카오 로그인 정보로 가입 여부 결과 발송(debug에서는 'code' 보낼것)",
    request_body=SwaggerKakaoLoginRequestSerializer(),
    responses={200: SwaggerKakaoCallbackResponseSerializer()}
)
@api_view(['POST'])
@permission_classes((AllowAny,))
def kakao_login_callback(request):
    code = request.data.get('code')
    access_token = request.data.get('access_token')

    if code is not None and access_token is None:
        token_response = requests.post(
            "https://kauth.kakao.com/oauth/token",
            data={
                "grant_type": "authorization_code",
                "client_id": KAKAO_REST_API_KEY,
                "redirect_uri": KAKAO_REDIRECT_URL,
                "code": code,
            }
        )
        if token_response.status_code == 200:
            access_token = token_response.json()["access_token"]

    profile_request = requests.get(
        "https://kapi.kakao.com/v2/user/me",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    profile_json = profile_request.json()
    uid = str(profile_json.get('id'))

    try:
        SocialAccount.objects.get(provider="kakao", uid=uid)
        # 유저 정보가 있는 경우(로그인)
        return Response(data={"user_exists": True, "access_token": access_token}, status=status.HTTP_200_OK)
    except SocialAccount.DoesNotExist:
        # 유저 정보가 없는 경우(새로 가입)
        return Response(data={"user_exists": False, "access_token": access_token}, status=status.HTTP_200_OK)


class KakaoLogin(SocialLoginView):
    adapter_class = KakaoOAuth2Adapter
    client_class = OAuth2Client
    callback_url = redirect_url

    @swagger_auto_schema(
        operation_id='카카오 로그인 완료',
        operation_description='유저가 존재하면 해당 user 정보를 반환하고, 존재하지 않으면 만들어서 반환',
        request_body=SwaggerKakaoLoginRequestSerializer,
        responses={200: SwaggerKakaoLoginFinishResponseSerializer()}
    )
    def post(self, request, *args, **kwargs):
        return super(KakaoLogin, self).post(request, *args, **kwargs)

