from django.contrib import admin

from cafe.serializers import CafeSerializer
from notification.firebase_message import FirebaseMessage
from notification.models import PushNotificationType
from request.models import CafeAdditionRequest, CafeInformationSuggestion


@admin.register(CafeAdditionRequest)
class CafeAdditionRequestAdmin(admin.ModelAdmin):
    list_display = ("id", "nickname", "cafe_name", "requested_at", "answered_at", "is_approved", "is_notified",)
    list_filter = ("user__profile__nickname", "is_approved",)
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
        cafe_serializer = CafeSerializer(obj.cafe, data={"is_visible": obj.is_approved}, partial=True)
        cafe_serializer.is_valid(raise_exception=True)
        cafe_serializer.save()
        if obj.is_notified:
            approve_title = "승인" if obj.is_approved else "거절"
            if obj.is_approved:
                approve_body = f"{obj.cafe.name} 등록요청이 승인되었습니다. 혼잡도를 공유하고 포인트 받아가세요!"
            else:
                approve_body = f"{obj.cafe.name} 등록요청이 거절되었습니다. 사유: {obj.rejection_reason}"
            FirebaseMessage.push_message(
                title=f"카페 등록요청 {approve_title} 알림",
                body=approve_body,
                push_type=PushNotificationType.Etc.value,
                user_object=obj.user,
                make_push_model=True
            )


@admin.register(CafeInformationSuggestion)
class CafeInformationSuggestionAdmin(admin.ModelAdmin):
    list_display = ("id", "nickname", "cafe_name", "is_open", "suggested_cafe_name", "suggested_new_image", "requested_at", "answered_at", "is_approved", "is_notified",)
    list_filter = ("user__profile__nickname", "is_approved",)
    search_fields = ("user__profile__nickname",)
    date_hierarchy = "requested_at"
    ordering = ("-requested_at",)
    list_select_related = ["cafe", "suggested_cafe", "suggested_new_image", "user"]
    save_as = True
    preserve_filters = True

    def nickname(self, request): return request.user.profile.nickname

    def cafe_name(self, request): return request.cafe.name if request.cafe else None

    def suggested_cafe_name(self, request):
        return request.suggested_cafe.name if request.suggested_cafe else None

    nickname.short_description = "요청자"
    cafe_name.short_description = "요청 카페"
    suggested_cafe_name.short_description = "수정 요청한 카페 정보"

    def delete_model(self, request, obj):
        self.s3_manager.delete_image(path=obj.suggested_new_image)
        obj.delete()

    def delete_queryset(self, request, queryset):
        for obj in queryset:
            self.s3_manager.delete_image(path=obj.suggested_new_image)
            obj.delete()


# @admin.register(WithdrawalRequest)
# class WithdrawalRequestAdmin(admin.ModelAdmin):
#     list_display = ("id", "nickname", "requested_at", "reason",)
#     list_filter = ("reason",)
#     date_hierarchy = "requested_at"
#     search_fields = ("user__profile__nickname",)
#     ordering = ("-requested_at",)
#     list_select_related = ["user"]
#     save_as = True
#     preserve_filters = True
#
#     def nickname(self, request): return request.user.profile.nickname if request.user else None
#
#     nickname.short_description = "요청자"
#
#
# @admin.register(UserMigrationRequest)
# class UserMigrationRequestAdmin(admin.ModelAdmin):
#     list_display = ("id", "nickname", "requested_at", "phone_number", "is_completed", "is_notified")
#     list_filter = ("is_completed",)
#     date_hierarchy = "requested_at"
#     search_fields = ("user__profile__nickname",)
#     ordering = ("-requested_at",)
#     list_select_related = ["user"]
#     save_as = True
#     preserve_filters = True
#
#     def nickname(self, request): return request.user.profile.nickname if request.user else None
#
#     nickname.short_description = "요청자"
