from django.contrib import admin

from app_config.models import Version


@admin.register(Version)
class VersionAdmin(admin.ModelAdmin):
    list_display = ("id", "major", "minor", "patch", "updated_at", "description")
    list_filter = ("major", "minor", "patch")
    ordering = ("-updated_at",)
    save_as = True
    preserve_filters = True
