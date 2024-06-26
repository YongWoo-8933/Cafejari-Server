import datetime
import os
import time
import uuid

import requests
from django.contrib import admin
from django.core.files.base import ContentFile

from cafe.models import Cafe
from cafe.serializers import CafeSerializer, CafeImageSerializer
from cafejari.settings import GOOGLE_PLACE_API_KEY
from notification.firebase_message import FirebaseMessage
from notification.models import PushNotificationType
from request.models import CafeAdditionRequest, CafeInformationSuggestion, WithdrawalRequest, UserMigrationRequest, \
    AppFeedback
from request.serializers import CafeAdditionRequestSerializer, CafeInformationSuggestionSerializer
from user.serializers import ProfileSerializer


@admin.register(CafeAdditionRequest)
class CafeAdditionRequestAdmin(admin.ModelAdmin):
    list_display = ("id", "nickname", "cafe_name", "requested_at", "answered_at", "point", "is_approved", "is_notified",)
    list_filter = ("user__profile__nickname", "is_approved",)
    autocomplete_fields = ("user", "cafe")
    search_fields = ("user__profile__nickname",)
    date_hierarchy = "requested_at"
    ordering = ("-requested_at",)
    list_select_related = ["cafe", "user"]
    save_as = True
    preserve_filters = True

    def nickname(self, request): return request.user.profile.nickname

    def cafe_name(self, request): return request.cafe.name if request.cafe else None

    nickname.short_description = "요청자"
    cafe_name.short_description = "요청 카페"

    def save_model(self, request, obj, form, change):
        obj.save()
        serializer = CafeAdditionRequestSerializer(obj, data={"answered_at": datetime.datetime.now()}, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        if obj.is_approved:
            # 카페 정보 저장
            cafe_serializer = CafeSerializer(obj.cafe, data={"is_visible": True}, partial=True)
            cafe_serializer.is_valid(raise_exception=True)
            cafe_serializer.save()

            # 포인트 추가
            if obj.point:
                serializer = ProfileSerializer(
                    obj.user.profile,
                    data={"point": obj.user.profile.point + obj.point},
                    partial=True
                )
                serializer.is_valid(raise_exception=True)
                serializer.save()

            # cafe image 설정
            if obj.cafe.google_place_id:
                url = "https://maps.googleapis.com/maps/api/place/details/json"
                params = {"place_id": obj.cafe.google_place_id, "key": GOOGLE_PLACE_API_KEY}
                references = []
                try:
                    response = requests.get(url=url, params=params)
                    if response.status_code == 200:
                        result_json = response.json()
                        if 'result' in result_json and 'photos' in result_json['result']:
                            photo_raw_json_list = result_json['result']['photos']
                            references = [e['photo_reference'] for e in photo_raw_json_list]
                except Exception:
                    pass

                url = "https://maps.googleapis.com/maps/api/place/photo"
                for reference in references:
                    params = {
                        "key": GOOGLE_PLACE_API_KEY,
                        "photo_reference": reference,
                        "maxwidth": 1200,
                        "maxheight": 1200
                    }
                    try:
                        response = requests.get(url=url, params=params)
                        if response.status_code == 200:

                            temp_file_name = f"temp_{str(uuid.uuid1())}.jpeg"
                            with open(temp_file_name, 'wb') as file:
                                for chunk in response.iter_content(1024):
                                    file.write(chunk)
                            time.sleep(0.4)
                            with open(temp_file_name, 'rb') as f:
                                image = ContentFile(f.read(), name=temp_file_name)

                            cafe_image_serializer = CafeImageSerializer(data={
                                "cafe": obj.cafe.id,
                                "image": image
                            })
                            cafe_image_serializer.is_valid(raise_exception=True)
                            cafe_image_serializer.save()
                            os.remove(temp_file_name)
                        else:
                            continue
                    except requests.Timeout:
                        continue
                    except requests.RequestException:
                        continue

        if obj.is_notified:
            if obj.is_approved and obj.point:
                message = f"{obj.cafe.name} 등록요청이 승인되어 {obj.point}P 지급되었습니다. 혼잡도를 등록하고 포인트 받아가세요!"
            elif obj.is_approved:
                message = f"{obj.cafe.name} 등록요청이 승인되었습니다. 혼잡도를 등록하고 포인트 받아가세요!"
            else:
                message = f"{obj.cafe.name} 등록요청이 거절되었습니다. 사유: {obj.rejection_reason}"
            FirebaseMessage.push_message(
                title=f"카페 등록요청 {'승인' if obj.is_approved else '거절'} 알림",
                body=message,
                push_type=PushNotificationType.Etc.value,
                user_object=obj.user,
                save_model=True
            )


@admin.register(CafeInformationSuggestion)
class CafeInformationSuggestionAdmin(admin.ModelAdmin):
    list_display = ("id", "nickname", "cafe_name", "suggested_cafe_name", "requested_at", "answered_at", "is_approved", "is_notified", "description")
    list_filter = ("is_approved",)
    autocomplete_fields = ("user", "suggested_cafe", "cafe")
    search_fields = ("user__profile__nickname", "cafe__name",)
    date_hierarchy = "requested_at"
    ordering = ("-requested_at",)
    list_select_related = ["cafe", "suggested_cafe", "user"]
    save_as = True
    preserve_filters = True

    def nickname(self, request): return request.user.profile.nickname

    def cafe_name(self, request): return request.cafe.name if request.cafe else None

    def suggested_cafe_name(self, request):
        return request.suggested_cafe.name if request.suggested_cafe else None

    def delete_model(self, request, obj):
        try:
            Cafe.objects.get(id=obj.suggested_cafe.id).delete()
        except Cafe.DoesNotExist:
            pass
        obj.delete()

    def delete_queryset(self, request, queryset):
        for obj in queryset:
            try:
                Cafe.objects.get(id=obj.suggested_cafe.id).delete()
            except Cafe.DoesNotExist:
                pass
            obj.delete()
        queryset.delete()

    nickname.short_description = "요청자"
    cafe_name.short_description = "요청 카페"
    suggested_cafe_name.short_description = "수정 요청한 카페 정보"

    def save_model(self, request, obj, form, change):
        obj.save()
        serializer = CafeInformationSuggestionSerializer(obj, data={"answered_at": datetime.datetime.now()}, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        if obj.is_notified:
            approve_title = "승인" if obj.is_approved else "거절"
            if obj.is_approved:
                approve_body = f"{obj.cafe.name} 정보 수정이 완료되었습니다."
            else:
                approve_body = f"{obj.cafe.name} 정보 수정 요청이 거절되었습니다. 사유: {obj.rejection_reason}"
            FirebaseMessage.push_message(
                title=f"카페 정보 수정 요청 {approve_title} 알림",
                body=approve_body,
                push_type=PushNotificationType.Etc.value,
                user_object=obj.user,
                save_model=True
            )


@admin.register(WithdrawalRequest)
class WithdrawalRequestAdmin(admin.ModelAdmin):
    list_display = ("id", "nickname", "requested_at", "reason",)
    list_filter = ("reason",)
    autocomplete_fields = ("user",)
    date_hierarchy = "requested_at"
    search_fields = ("user__profile__nickname",)
    ordering = ("-requested_at",)
    list_select_related = ["user"]
    save_as = True
    preserve_filters = True

    def nickname(self, request): return request.user.profile.nickname if request.user else None

    nickname.short_description = "요청자"


@admin.register(UserMigrationRequest)
class UserMigrationRequestAdmin(admin.ModelAdmin):
    list_display = ("id", "nickname", "requested_at", "phone_number", "is_completed", "is_notified")
    list_filter = ("is_completed",)
    autocomplete_fields = ("user",)
    date_hierarchy = "requested_at"
    search_fields = ("user__profile__nickname",)
    ordering = ("-requested_at",)
    list_select_related = ["user"]
    save_as = True
    preserve_filters = True

    def nickname(self, request): return request.user.profile.nickname if request.user else None

    nickname.short_description = "요청자"


@admin.register(AppFeedback)
class AppFeedbackAdmin(admin.ModelAdmin):
    list_display = ("id", "time", "feedback", "nickname")
    list_filter = ("feedback",)
    autocomplete_fields = ("user",)
    date_hierarchy = "time"
    search_fields = ("user__profile__nickname", "feedback")
    ordering = ("-time",)
    list_select_related = ["user"]
    save_as = True
    preserve_filters = True

    def nickname(self, feedback): return feedback.user.profile.nickname if feedback.user else None

    nickname.short_description = "사용자"
