
from django.contrib import admin
from django.utils.html import format_html

from notification.firebase_message import FirebaseMessage
from notification.models import PushNotification, PopUpNotification
from utils import replace_image_domain


@admin.register(PushNotification)
class PushNotificationAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "pushed_at", "type", "user_name", "is_read")
    list_filter = ("type",)
    autocomplete_fields = ("user","user__profile__nickname")
    search_fields = ("title", "body")
    ordering = ("-pushed_at",)
    date_hierarchy = "pushed_at"
    save_as = True
    preserve_filters = True

    def save_model(self, request, obj, form, change):
        obj.save()
        FirebaseMessage.push_message(
            title=obj.title,
            body=obj.body,
            push_type=obj.type,
            user_object=obj.user,
            save_model=False
        )

    def user_name(self, notification): return notification.user.profile.nickname if notification.user.profile else None

    user_name.short_description = "수신자"


@admin.register(PopUpNotification)
class PopUpNotificationAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "order", "image_tag", "visible", "datetime",)
    list_filter = ("visible",)
    search_fields = ("title",)
    ordering = ("order",)
    date_hierarchy = "datetime"
    save_as = True
    preserve_filters = True

    @staticmethod
    def image_tag(challenge):
        return format_html('<img src="{}" width="85" height="85" />', replace_image_domain(challenge.image.url))

