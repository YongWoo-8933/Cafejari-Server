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

