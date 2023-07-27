
from django.contrib import admin
from django.utils.html import format_html

from user.models import User, Profile, Grade, ProfileImage
from utils import ImageModelAdmin, replace_image_domain


@admin.register(Grade)
class GradeAdmin(ImageModelAdmin):
    list_display = ("step", "image_tag", "name", "description")
    list_filter = ("step",)
    search_fields = ("name",)
    ordering = ("step",)
    save_as = True
    preserve_filters = True

    def image_tag(self, grade):
        return format_html('<img src="{}" width="85" height="85" />', replace_image_domain(grade.image.url)) if grade.image else None

    image_tag.short_description = "이미지"


class ProfileInline(admin.TabularInline):
    model = Profile


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "nickname", "image_tag", "email", "grade", "last_login", "date_joined", "is_active", "social_type", "point")
    list_filter = ("is_active", "profile__grade__name")
    search_fields = ("profile__nickname", "username", "email", "first_name", "last_name",)
    ordering = ("-date_joined",)
    inlines = (ProfileInline,)
    date_hierarchy = "date_joined"
    list_select_related = ["profile"]
    save_as = True
    preserve_filters = True

    def nickname(self, user): return user.profile.nickname if user.profile else None

    def image_tag(self, user):
        return format_html('<img src="{}" width="85" height="85" />', replace_image_domain(user.profile.profile_image.image.url)) if user.profile.profile_image else None

    def grade(self, user): return user.profile.grade.name if user.profile.grade else None

    def social_type(self, user): return user.socialaccount_set.first().provider if user.socialaccount_set.first() else None

    def point(self, user): return user.profile.point if user.profile else None

    nickname.short_description = "닉네임"
    image_tag.short_description = "이미지"
    grade.short_description = '등급'
    social_type.short_description = '소셜타입'
    point.short_description = '포인트'


@admin.register(ProfileImage)
class ProfileImageAdmin(ImageModelAdmin):
    list_display = ("id", "is_default", "image_tag")
    list_filter = ("is_default",)
    save_as = True
    preserve_filters = True

    def image_tag(self, profile_image):
        return format_html('<img src="{}" width="85" height="85" />', replace_image_domain(profile_image.image.url))

    image_tag.short_description = "이미지"
