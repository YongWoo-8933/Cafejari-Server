from enum import Enum

from django.db import models
from django.utils import timezone


class CafeAdditionRequest(models.Model):
    is_approved = models.BooleanField(default=False)
    is_notified = models.BooleanField(default=False)
    requested_at = models.DateTimeField(auto_now_add=True)
    answered_at = models.DateTimeField(default=timezone.now)
    etc = models.TextField(default=None, null=True, blank=True)
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
    etc = models.TextField(default=None, null=True, blank=True)
    description = models.TextField(default=None, null=True, blank=True)
    rejection_reason = models.TextField(default=None, null=True, blank=True)
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



class WithdrawalReason(Enum):
    NoCafe = "카페"
    OccupancyRate = "혼잡도"
    AppUse = "앱사용"
    Design = "디자인"
    Etc = "기타"


class WithdrawalRequest(models.Model):
    requested_at = models.DateTimeField(auto_now_add=True)
    reason = models.CharField(max_length=63, choices=((reason.value, reason.value) for reason in WithdrawalReason))
    user = models.ForeignKey(
        'user.User',
        on_delete=models.SET_NULL,
        related_name="withdrawal_request",
        db_column="user",
        default=None,
        blank=True,
        null=True
    )

    class Meta:
        db_table = 'request_withdrawal_request'
        db_table_comment = '회원탈퇴 요청'
        app_label = 'request'
        ordering = ["-requested_at"]


class UserMigrationRequest(models.Model):
    requested_at = models.DateTimeField(auto_now_add=True)
    phone_number = models.CharField(max_length=8)
    is_completed = models.BooleanField(default=False)
    is_notified = models.BooleanField(default=False)
    user = models.ForeignKey(
        'user.User',
        on_delete=models.SET_NULL,
        related_name="user_migration_request",
        db_column="user",
        default=None,
        blank=True,
        null=True
    )

    class Meta:
        db_table = 'user_migration_request'
        db_table_comment = '사용자 정보이전 요청'
        app_label = 'request'
        ordering = ["-requested_at"]
