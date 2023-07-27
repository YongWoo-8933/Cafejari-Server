from django.contrib import admin
from django.utils.html import format_html

from cafe.models import Cafe, Brand, District, OpeningHour, CafeFloor, CafeImage, OccupancyRatePrediction, \
    OccupancyRateUpdateLog, CongestionArea, CafeVIP, CafeTypeTag, DailyActivityStack
from utils import ImageModelAdmin, replace_image_domain


@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    list_display = ("id", "city", "gu", "dong", "latitude", "longitude",)
    list_filter = ("city", "gu", "dong")
    search_fields = ("city", "gu", "dong")
    ordering = ("city", "gu", "dong")
    save_as = True
    preserve_filters = True


@admin.register(CongestionArea)
class CongestionAreaAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "category", "current_congestion", "south_west_latitude", "south_west_longitude", "north_east_latitude", "north_east_longitude")
    list_filter = ("category", "current_congestion")
    search_fields = ("name", "category",)
    ordering = ("category", "name",)
    save_as = True
    preserve_filters = True


@admin.register(Brand)
class BrandAdmin(ImageModelAdmin):
    list_display = ("id", "image_tag", "name", "has_item")
    list_filter = ("has_item",)
    search_fields = ("name",)
    ordering = ("name",)
    save_as = True
    preserve_filters = True

    def image_tag(self, brand):
        return format_html('<img src="{}" width="85" height="85" />', replace_image_domain(brand.image.url)) if brand.image else None

    image_tag.short_description = "이미지"


@admin.register(CafeTypeTag)
class CafeTypeTagAdmin(admin.ModelAdmin):
    list_display = ("id", "cafe_name", "nickname", "custom_has_openness", "custom_is_coffee_focused", "custom_is_work_friendly",)
    list_filter = ("cafe__brand__name", "has_openness", "is_coffee_focused", "is_work_friendly",)
    search_fields = ("cafe__name", "user__profile__nickname",)
    ordering = ("cafe__name",)
    list_select_related = ["cafe", "user"]
    save_as = True
    preserve_filters = True

    def cafe_name(self, tag): return tag.cafe.name

    def nickname(self, tag): return tag.user.profile.nickname if tag.user else None

    def custom_has_openness(self, tag): return "개방감" if tag.has_openness else "아늑함"

    def custom_is_coffee_focused(self, tag): return "커피주력" if tag.is_coffee_focused else "디저트주력"

    def custom_is_work_friendly(self, tag): return "공부/업무" if tag.is_work_friendly else "감성/사진"

    cafe_name.short_description = "카페"
    nickname.short_description = "닉네임"
    custom_has_openness.short_description = "개방/아늑"
    custom_is_coffee_focused.short_description = "커피/디저트"
    custom_is_work_friendly.short_description = "공부/감성성"


class OpeningHourInline(admin.TabularInline):
    model = OpeningHour


class CafeFloorInline(admin.TabularInline):
    model = CafeFloor


class CafeImageInline(admin.TabularInline):
    model = CafeImage


@admin.register(Cafe)
class CafeAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "floor_count", "district_city", "brand_name", "congestion_area", "address", "is_visible", "is_closed",)
    list_filter = ("is_visible", "is_closed", "brand__name", "district__city", "congestion_area__name")
    search_fields = ("name", "address",)
    ordering = ("is_visible", "-is_closed", "name",)
    inlines = (OpeningHourInline, CafeFloorInline, CafeImageInline,)
    list_select_related = ["district", "brand", "opening_hour"]
    save_as = True
    preserve_filters = True

    def floor_count(self, cafe): return len(cafe.cafe_floor.all())

    def district_city(self, cafe): return cafe.district.city if cafe.district else None

    def congestion_area(self, cafe): return cafe.congestion_area.name if cafe.congestion_area else None

    def brand_name(self, cafe): return cafe.brand.name if cafe.brand else None

    floor_count.short_description = "층수"
    district_city.short_description = "구역"
    congestion_area.short_description = "혼잡도 지역"
    brand_name.short_description = "브랜드"


@admin.register(CafeImage)
class CafeImageAdmin(ImageModelAdmin):
    list_display = ("id", "cafe_name", "image_tag", "is_visible",)
    list_filter = ("cafe__name", "is_visible",)
    search_fields = ("cafe__name",)
    ordering = ("cafe__name",)
    list_select_related = ["cafe"]
    save_as = True
    preserve_filters = True

    def image_tag(self, cafe_image):
        return format_html('<img src="{}" width="85" height="85" />', replace_image_domain(cafe_image.image.url)) if cafe_image.image else None

    def cafe_name(self, cafe_image): return cafe_image.cafe.name

    image_tag.short_description = "이미지"
    cafe_name.short_description = "카페"


@admin.register(CafeVIP)
class CafeVIPAdmin(admin.ModelAdmin):
    list_display = ("id", "cafe_name", "nickname", "update_count",)
    list_filter = ("cafe__name", "user__profile__nickname",)
    search_fields = ("cafe__name", "user__profile__nickname",)
    ordering = ("cafe__name", "-update_count")
    list_select_related = ["cafe", "user"]
    save_as = True
    preserve_filters = True

    def cafe_name(self, vip): return vip.cafe.name

    def nickname(self, vip): return vip.user.profile.nickname

    cafe_name.short_description = "카페"
    nickname.short_description = "닉네임"


@admin.register(OccupancyRatePrediction)
class OccupancyRatePredictionAdmin(admin.ModelAdmin):
    list_display = ("id", "cafe_name", "occupancy_rate", "update")
    list_filter = ("cafe_floor__cafe__name", "cafe_floor__cafe__brand__name", "cafe_floor__cafe__district__city",)
    list_select_related = ["cafe_floor"]
    date_hierarchy = "update"
    search_fields = ("cafe_floor__cafe__name",)
    ordering = ("-update",)
    save_as = True
    preserve_filters = True

    def cafe_name(self, prediction): return prediction.cafe_floor.cafe.name if prediction.cafe_floor else None

    cafe_name.short_description = "카페"


@admin.register(OccupancyRateUpdateLog)
class OccupancyRateUpdateLogAdmin(admin.ModelAdmin):
    list_display = ("id", "cafe_name_floor", "nickname", "occupancy_rate", "update", "point", "is_notified")
    list_filter = ("cafe_floor__cafe__name", "user__profile__nickname")
    date_hierarchy = "update"
    search_fields = ("user__profile__nickname", "cafe_floor__cafe__name")
    ordering = ("-update",)
    save_as = True
    preserve_filters = True

    def nickname(self, log): return log.user.profile.nickname if log.user else None

    def cafe_name_floor(self, log):
        return f"{log.cafe_floor.cafe.name} {log.cafe_floor.floor}층"  if log.cafe_floor else None

    nickname.short_description = "닉네임"
    cafe_name_floor.short_description = "카페/층"


@admin.register(DailyActivityStack)
class DailyActivityStackAdmin(admin.ModelAdmin):
    list_display = ("id", "cafe_name_floor", "nickname", "update")
    date_hierarchy = "update"
    search_fields = ("user__profile__nickname", "cafe_floor__cafe__name")
    ordering = ("-update",)
    save_as = True
    preserve_filters = True

    def nickname(self, stack): return stack.user.profile.nickname if stack.user.profile else None

    def cafe_name_floor(self, stack):
        return f"{stack.cafe_floor.cafe.name} {stack.cafe_floor.floor}층"

    nickname.short_description = "닉네임"
    cafe_name_floor.short_description = "카페/층"
