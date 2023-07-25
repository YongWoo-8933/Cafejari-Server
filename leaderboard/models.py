from django.db import models


class TotalSharingRanker(models.Model):
    sharing_count = models.IntegerField()
    user = models.OneToOneField(
        'user.User',
        on_delete=models.CASCADE,
        related_name="total_sharing_ranker",
        db_column="user",
    )

    class Meta:
        db_table = 'leaderboard_total_sharing_ranker'
        db_table_comment = '누적 공유 활동 랭커'
        app_label = 'leaderboard'
        ordering = ["-sharing_count"]


class MonthSharingRanker(models.Model):
    sharing_count = models.IntegerField()
    user = models.OneToOneField(
        'user.User',
        on_delete=models.CASCADE,
        related_name="month_sharing_ranker",
        db_column="user",
    )

    class Meta:
        db_table = 'leaderboard_month_sharing_ranker'
        db_table_comment = '월간 공유 활동 랭커'
        app_label = 'leaderboard'
        ordering = ["-sharing_count"]


class WeekSharingRanker(models.Model):
    sharing_count = models.IntegerField()
    user = models.OneToOneField(
        'user.User',
        on_delete=models.CASCADE,
        related_name="week_sharing_ranker",
        db_column="user",
    )

    class Meta:
        db_table = 'leaderboard_week_sharing_ranker'
        db_table_comment = '주간 공유 활동 랭커'
        app_label = 'leaderboard'
        ordering = ["-sharing_count"]


class MonthlyHotCafeLog(models.Model):
    date = models.DateField(unique=True, auto_now_add=True)
    cafe_log = models.OneToOneField(
        'cafe_log.CafeLog',
        on_delete=models.SET_NULL,
        related_name="monthly_hot_cafe_log",
        db_column="cafe_log",
        default=None,
        blank=True,
        null=True
    )

    class Meta:
        db_table = 'leaderboard_monthly_hot_cafe_log'
        db_table_comment = '이달의 카페로그'
        app_label = 'leaderboard'
        ordering = ["-date"]
