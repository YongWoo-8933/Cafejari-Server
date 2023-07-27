from django.contrib import admin
from django.utils.html import format_html

from cafe_log.models import CafeLog, CafeLogReport, Snapshot, CafeLogLike
from utils import ImageModelAdmin, replace_image_domain


@admin.register(CafeLog)
class CafeLogAdmin(admin.ModelAdmin):
    list_display = ("id", "image_tag", "cafe_name", "user_nickname", "theme", "like_count", "created_at", "updated_at", "report_count", "is_private", "is_visible")
    list_filter = ("is_private", "is_visible", "theme")
    list_select_related = ["cafe", "user", "snapshot"]
    search_fields = ("cafe__name", "user__profile__nickname", "content")
    date_hierarchy = "created_at"
    ordering = ("-created_at",)
    save_as = True
    preserve_filters = True

    def image_tag(self, log):
        return format_html('<img src="{}" width="85" height="85" />', replace_image_domain(log.snapshot.image.url)) if log.snapshot else None

    def cafe_name(self, log):
        return log.cafe.name if log.cafe else None

    def user_nickname(self, log):
        return log.user.profile.nickname if log.user else None

    def like_count(self, log): return len(log.like.all())

    def report_count(self, log): return len(log.cafe_log_report.all())

    image_tag.short_description = "이미지"
    cafe_name.short_description = "카페"
    user_nickname.short_description = "닉네임"
    like_count.short_description = "좋아요 수"
    report_count.short_description = "신고 수"


@admin.register(CafeLogReport)
class CafeLogReportAdmin(admin.ModelAdmin):
    list_display = ("id", "image_tag", "reporter", "reason")
    list_select_related = ["cafe_log", "user"]
    search_fields = ("cafe_log__cafe__name", "user__profile__nickname", "reason")
    date_hierarchy = "cafe_log__created_at"
    ordering = ("-cafe_log__created_at",)
    save_as = True
    preserve_filters = True

    def image_tag(self, report):
        return format_html('<img src="{}" width="85" height="85" />', replace_image_domain(report.cafe_log.snapshot.image.url)) if report.cafe_log.snapshot else None

    def reporter(self, report):
        return report.user.profile.nickname if report.user.profile else None

    image_tag.short_description = "이미지"
    reporter.short_description = "신고자"


@admin.register(CafeLogLike)
class CafeLogReportAdmin(admin.ModelAdmin):
    list_display = ("id", "image_tag", "user_nickname", "cafe_name")
    list_select_related = ["cafe_log", "user"]
    search_fields = ("cafe_log__cafe__name", "user__profile__nickname")
    date_hierarchy = "cafe_log__created_at"
    ordering = ("-cafe_log__created_at",)
    save_as = True
    preserve_filters = True

    def image_tag(self, like):
        return format_html('<img src="{}" width="85" height="85" />', replace_image_domain(like.cafe_log.snapshot.image.url)) if like.cafe_log.snapshot else None

    def user_nickname(self, like):
        return like.user.profile.nickname if like.user.profile else None

    def cafe_name(self, like):
        return like.cafe_log.cafe.name if like.cafe_log.cafe else None

    image_tag.short_description = "이미지"
    user_nickname.short_description = "추천자"
    cafe_name.short_description = "카페명"


@admin.register(Snapshot)
class SnapshotAdmin(ImageModelAdmin):
    list_display = ("id", "image_tag", "theme")
    list_filter = ("theme",)
    save_as = True
    preserve_filters = True

    def image_tag(self, snapshot):
        return format_html('<img src="{}" width="85" height="85" />', replace_image_domain(snapshot.image.url)) if snapshot.image else None

    image_tag.short_description = "이미지"


