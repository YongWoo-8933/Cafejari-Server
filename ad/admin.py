from django.contrib.gis import admin
from ad.models import AdLog


@admin.register(AdLog)
class AdLogAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "date", "count", "description",)
    list_filter = ("name",)
    date_hierarchy = "date"
    search_fields = ("name", "description",)
    ordering = ("-date", "name",)
    save_as = True
    preserve_filters = True

    def get_readonly_fields(self, request, obj=None):
        return self.readonly_fields + ('name', 'date', 'count', 'description')

    def has_add_permission(self, request):
        return False
