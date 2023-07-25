from enum import Enum

from django.db import models


def snapshot_image_upload_path(instance, filename):
    if instance.theme == CafeLogTheme.Free.value:
        cafe_log = instance.cafe_log.all()[0]
        return f"cafe_log/{instance.theme}/{cafe_log.posted_at.year}/{cafe_log.posted_at.month}/{cafe_log.posted_at.day}/{instance.cafe.name}_스냅샷_{filename}"
    else:
        return f"cafe_log/{instance.theme}/default_image_{filename}"


class CafeLogTheme(Enum):
    Work = "카공/업무"
    Meeting = "만남"
    Healing = "힐링"
    Free = "자유"


class CafeLog(models.Model):
    is_private = models.BooleanField(default=False)
    is_visible = models.BooleanField(default=True)
    theme = models.CharField(choices=((theme.value, theme.value) for theme in CafeLogTheme))
    content = models.CharField(max_length=63)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    cafe = models.ForeignKey(
        'cafe.Cafe',
        on_delete=models.SET_NULL,
        related_name="cafe_log",
        db_column="cafe",
        default=None,
        blank=True,
        null=True
    )
    snapshot = models.ForeignKey(
        'Snapshot',
        on_delete=models.SET_NULL,
        related_name="cafe_log",
        db_column="snapshot",
        default=None,
        blank=True,
        null=True
    )
    user = models.ForeignKey(
        'user.User',
        on_delete=models.SET_NULL,
        related_name="cafe_log",
        db_column="user",
        default=None,
        blank=True,
        null=True
    )

    class Meta:
        db_table = 'cafe_log_cafe_log'
        db_table_comment = '카페로그 모델'
        app_label = 'cafe_log'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=["created_at"], name="cafe_log_created_time_index"),
            models.Index(fields=["updated_at"], name="cafe_log_updated_time_index"),
        ]


class CafeLogReport(models.Model):
    reason = models.TextField()
    cafe_log = models.ForeignKey(
        'CafeLog',
        on_delete=models.CASCADE,
        related_name="cafe_log_report",
        db_column="cafe_log",
    )
    user = models.ForeignKey(
        'user.User',
        on_delete=models.CASCADE,
        related_name="cafe_log_report",
        db_column="user"
    )

    class Meta:
        db_table = 'cafe_log_cafe_log_report'
        db_table_comment = '카페로그 신고 모델'
        app_label = 'cafe_log'
        ordering = ['-cafe_log__created_at']


class Snapshot(models.Model):
    theme = models.CharField(choices=((theme.value, theme.value) for theme in CafeLogTheme))
    image = models.ImageField(upload_to=snapshot_image_upload_path)

    class Meta:
        db_table = 'cafe_log_snapshot'
        db_table_comment = '카페로그 속 사진 모델'
        app_label = 'cafe_log'


class CafeLogLike(models.Model):
    cafe_log = models.ForeignKey(
        'CafeLog',
        on_delete=models.CASCADE,
        related_name="like",
        db_column="cafe_log",
    )
    user = models.ForeignKey(
        'user.User',
        on_delete=models.CASCADE,
        related_name="like",
        db_column="user"
    )

    class Meta:
        db_table = 'cafe_log_like'
        db_table_comment = '카페로그 좋아요 모델'
        app_label = 'cafe_log'
        ordering = ['-cafe_log__created_at']
