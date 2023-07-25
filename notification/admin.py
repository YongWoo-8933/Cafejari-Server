
from django.contrib import admin
from django.core.exceptions import ObjectDoesNotExist

from notification.firebase_message import FirebaseMessage
from notification.models import PushNotification
from user.models import User


@admin.register(PushNotification)
class PushNotificationAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "pushed_at", "type", "get_users")
    list_filter = ("type",)
    search_fields = ("title", "body")
    ordering = ("-pushed_at",)
    date_hierarchy = "pushed_at"
    save_as = True
    preserve_filters = True

    def save_model(self, request, obj, form, change):
        obj.save()
        user_object_list = [User.objects.get(id=user_id) for user_id in request.POST.getlist('user')]
        FirebaseMessage.push_messages(
            title=obj.title,
            body=obj.body,
            push_type=obj.type,
            user_object_list=user_object_list,
            make_push_model=False
        )

    def get_users(self, notification):
        user_nicknames = []
        for user in notification.user.all():
            try:
                user_nicknames.append(user.profile.nickname)
            except ObjectDoesNotExist:
                continue
        return ", ".join(nickname for nickname in user_nicknames)

    get_users.short_description = "수신자들"

