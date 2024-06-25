from django.contrib import admin
from django.utils.html import format_html

from leaderboard.models import TotalSharingRanker, MonthSharingRanker, WeekSharingRanker, \
    MonthlyHotCafeLog


@admin.register(TotalSharingRanker)
class TotalSharingRankerAdmin(admin.ModelAdmin):
    list_display = ("id", "sharing_count", "user_nickname",)
    autocomplete_fields = ("user",)
    search_fields = ("user__profile__nickname",)
    ordering = ("-sharing_count",)
    list_select_related = ["user"]
    save_as = True
    preserve_filters = True

    def user_nickname(self, ranker): return ranker.user.profile.nickname

    user_nickname.short_description = "닉네임"


@admin.register(MonthSharingRanker)
class MonthSharingRankerAdmin(admin.ModelAdmin):
    list_display = ("id", "sharing_count", "user_nickname",)
    autocomplete_fields = ("user",)
    search_fields = ("user__profile__nickname",)
    ordering = ("-sharing_count",)
    list_select_related = ["user"]
    save_as = True
    preserve_filters = True

    def user_nickname(self, ranker): return ranker.user.profile.nickname

    user_nickname.short_description = "닉네임"


@admin.register(WeekSharingRanker)
class WeekSharingRankerAdmin(admin.ModelAdmin):
    list_display = ("id", "sharing_count", "user_nickname",)
    autocomplete_fields = ("user",)
    search_fields = ("user__profile__nickname",)
    ordering = ("-sharing_count",)
    list_select_related = ["user"]
    save_as = True
    preserve_filters = True

    def user_nickname(self, ranker): return ranker.user.profile.nickname

    user_nickname.short_description = "닉네임"


@admin.register(MonthlyHotCafeLog)
class MonthlyHotCafeLogAdmin(admin.ModelAdmin):
    list_display = ("id", "date", "cafe_log_user_nickname", "cafe_log_snapshot_image_tag", "like_count",)
    search_fields = ("user__profile__nickname",)
    ordering = ("-date",)
    list_select_related = ["cafe_log"]
    save_as = True
    preserve_filters = True

    def cafe_log_snapshot_image_tag(self, hot_log):
        return format_html('<img src="{}" width="85" height="85" />', hot_log.cafe_log.snapshot.image.url) if hot_log.snapshot else None

    def cafe_log_user_nickname(self, hot_log):
        return hot_log.cafe_log.user.profile.nickname if hot_log.snapshot else None

    def like_count(self, hot_log):
        return len(hot_log.cafe_log.like.all()) if hot_log.snapshot else None

    cafe_log_snapshot_image_tag.short_description = "스냅샷 이미지"
    cafe_log_user_nickname.short_description = "스냅샷 작성자"
    like_count.short_description = "좋아요 수"

