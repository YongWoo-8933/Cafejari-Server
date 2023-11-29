
from django.contrib import admin
from django.core.exceptions import ObjectDoesNotExist

from notification.firebase_message import FirebaseMessage
from notification.models import PushNotification
from user.models import User


@admin.register(PushNotification)
class PushNotificationAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "pushed_at", "type", "user_name", "is_read")
    list_filter = ("type",)
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

