from enum import Enum

from django.db import models


class PushNotificationType(Enum):
    Notification = '공지'
    Activity = '활동'
    Event = '이벤트'
    Marketing = '마케팅'
    Etc = '기타'


class PushNotification(models.Model):
    title = models.CharField(max_length=31)
    body = models.TextField()
    pushed_at = models.DateTimeField(auto_now_add=True)
    type = models.CharField(choices=((push_type.value, push_type.value) for push_type in PushNotificationType))
    is_read = models.BooleanField(default=False)
    user = models.ForeignKey(
        'user.User',
        on_delete=models.CASCADE,
        related_name="push_notification",
        db_column="user",
        null=True,
        blank=True,
        default=None
    )

    class Meta:
        db_table = 'notification_push_notification'
        db_table_comment = '푸쉬 알림 모델'
        app_label = 'notification'
        ordering = ['-pushed_at']


class InAppRouteTarget(Enum):
    Map = '지도'
    MyCafe = '활동'
    Challenge = '챌린지'
    MyPage = '마이페이지'
    KakaoChannel = '카카오톡채널'


def pop_up_image_upload_path(instance, filename):
    return f"notification/{instance.datetime.year}/{instance.datetime.month}/{filename}"


class PopUpNotification(models.Model):
    order = models.IntegerField(null=True, default=None, blank=True)
    title = models.CharField(max_length=31, null=True, default=None, blank=True)
    visible = models.BooleanField(default=True)
    datetime = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to=pop_up_image_upload_path)
    web_view_url = models.URLField(max_length=255, null=True, default=None, blank=True)
    external_url = models.URLField(max_length=255, null=True, default=None, blank=True)
    in_app_route_target = models.IntegerField(
        choices=((index, tab.value) for index, tab in enumerate(InAppRouteTarget)),
        null=True, default=None, blank=True
    )
    cafe = models.ForeignKey(
        'cafe.Cafe',
        on_delete=models.SET_NULL,
        related_name="pop_up_notification",
        db_column="cafe",
        null=True,
        blank=True,
        default=None
    )
    challenge = models.ForeignKey(
        'challenge.Challenge',
        on_delete=models.SET_NULL,
        related_name="pop_up_notification",
        db_column="challenge",
        null=True,
        blank=True,
        default=None
    )

    class Meta:
        db_table = 'notification_pop_up_notification'
        db_table_comment = '팝업 모델'
        app_label = 'notification'
        ordering = ['-datetime']

