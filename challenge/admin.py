from django.contrib import admin
from django.utils.html import format_html

from challenge.models import Challenge, ChallengeMilestone, Challenger, ChallengePoint
from utils import ImageModelAdmin, replace_image_domain


class ChallengeMilestoneInline(admin.TabularInline):
    model = ChallengeMilestone


@admin.register(Challenge)
class ChallengeAdmin(ImageModelAdmin):
    list_display = ("id", "name", "image_tag", "url", "available", "start", "finish", "participant_limit", "goal")
    list_filter = ("available",)
    inlines = (ChallengeMilestoneInline,)
    search_fields = ("name",)
    date_hierarchy = "start"
    ordering = ("-start",)
    save_as = True
    preserve_filters = True

    def image_tag(self, challenge):
        return format_html('<img src="{}" width="85" height="85" />', replace_image_domain(challenge.image.url))

    def challenger_count(self, challenge): return len(challenge.challenger.all())

    def milestone_count(self, challenge): return len(challenge.challenge_milestone.all())

    image_tag.short_description = "이미지"
    challenger_count.short_description = "참가자 수"
    milestone_count.short_description = "목표지점 수"


class ChallengePointInline(admin.TabularInline):
    model = ChallengePoint


@admin.register(Challenger)
class ChallengerAdmin(admin.ModelAdmin):
    list_display = ("id", "user_nickname", "challenge_name", "image_tag", "progress_rate", "count")
    list_filter = ("challenge__available", "challenge__name")
    autocomplete_fields = ("challenge", "user")
    inlines = (ChallengePointInline,)
    search_fields = ("user__profile__nickname", "challenge__name")
    date_hierarchy = "challenge__start"
    ordering = ("-challenge__start",)
    save_as = True
    preserve_filters = True

    def image_tag(self, challenger):
        return format_html('<img src="{}" width="85" height="85" />', replace_image_domain(challenger.challenge.image.url))

    def challenge_name(self, challenger): return challenger.challenge.name

    def user_nickname(self, challenger): return challenger.user.profile.nickname if challenger.user.profile else None

    image_tag.short_description = "챌린지 이미지"
    challenge_name.short_description = "챌린지 이름"
    user_nickname.short_description = "닉네임"

