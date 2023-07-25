
from django.db import models
from django.utils import timezone


class CafeAdditionRequest(models.Model):
    is_approved = models.BooleanField(default=False)
    is_notified = models.BooleanField(default=False)
    requested_at = models.DateTimeField(auto_now_add=True)
    answered_at = models.DateTimeField(default=timezone.now)
    rejection_reason = models.TextField(default=None, null=True, blank=True)
    cafe = models.ForeignKey(
        'cafe.Cafe',
        on_delete=models.SET_NULL,
        related_name="cafe_addition_request",
        db_column="cafe",
        default=None,
        blank=True,
        null=True
    )
    user = models.ForeignKey(
        'user.User',
        on_delete=models.CASCADE,
        related_name="cafe_addition_request",
        db_column="user",
    )

    class Meta:
        db_table = 'request_cafe_addition_request'
        db_table_comment = '카페 등록 요청'
        app_label = 'request'
        ordering = ["-requested_at"]


class CafeInformationSuggestion(models.Model):
    is_approved = models.BooleanField(default=False)
    is_notified = models.BooleanField(default=False)
    requested_at = models.DateTimeField(auto_now_add=True)
    answered_at = models.DateTimeField(default=timezone.now)
    rejection_reason = models.TextField(default=None, null=True, blank=True)
    is_open = models.BooleanField(default=True)
    cafe = models.ForeignKey(
        'cafe.Cafe',
        on_delete=models.SET_NULL,
        related_name="cafe_information_suggestion",
        db_column="cafe",
        default=None,
        blank=True,
        null=True
    )
    suggested_cafe = models.ForeignKey(
        'cafe.Cafe',
        on_delete=models.SET_NULL,
        related_name="suggested_cafe_information_suggestion",
        db_column="suggested_cafe",
        default=None,
        blank=True,
        null=True
    )
    suggested_new_image = models.ForeignKey(
        'cafe.CafeImage',
        on_delete=models.SET_NULL,
        related_name="cafe_information_suggestion",
        db_column="suggested_new_image",
        default=None,
        blank=True,
        null=True
    )
    user = models.ForeignKey(
        'user.User',
        on_delete=models.CASCADE,
        related_name="cafe_information_suggestion",
        db_column="user",
    )

    class Meta:
        db_table = 'request_cafe_information_suggestion'
        db_table_comment = '카페 추가 정보 등록 요청'
        app_label = 'request'
        ordering = ["-requested_at"]
