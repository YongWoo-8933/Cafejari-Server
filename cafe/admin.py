from django.contrib.gis import admin
from django.contrib.gis.geos import Point
from django.utils.html import format_html

from cafe.models import Cafe, Brand, District, OpeningHour, CafeFloor, CafeImage, OccupancyRatePrediction, \
    OccupancyRateUpdateLog, CongestionArea, CafeVIP, DailyActivityStack, Location, CATI
from data.admin import OpeningHoursUpdateAdmin
from utils import ImageModelAdmin, replace_image_domain


@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    list_display = ("id", "city", "gu", "dong", "latitude", "longitude",)
    list_filter = ("city", "gu", "dong")
    search_fields = ("city", "gu", "dong")
    ordering = ("city", "gu", "dong")
    save_as = True
    preserve_filters = True


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "image_tag", "is_visible", "latitude", "longitude")
    search_fields = ("name",)
    list_filter = ("is_visible",)
    ordering = ("name",)
    save_as = True
    preserve_filters = True

    def image_tag(self, location):
        return format_html('<img src="{}" width="85" height="85" />', replace_image_domain(location.image.url)) if location.image else None

    image_tag.short_description = "이미지"


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


@admin.register(CATI)
class CATIAdmin(admin.ModelAdmin):
    list_display = ("id", "cafe_name", "nickname", "openness", "coffee", "workspace", "acidity",)
    list_filter = ("cafe__brand__name", "openness", "coffee", "workspace", "acidity",)
    autocomplete_fields = ("user", "user__profile__nickname", "cafe", "cafe__name")
    search_fields = ("cafe__name", "user__profile__nickname",)
    ordering = ("cafe__name",)
    list_select_related = ["cafe", "user"]
    save_as = True
    preserve_filters = True

    def cafe_name(self, cati): return cati.cafe.name

    def nickname(self, cati): return cati.user.profile.nickname if cati.user else None

    cafe_name.short_description = "카페"
    nickname.short_description = "닉네임"


class OpeningHourInline(admin.TabularInline):
    model = OpeningHour


class CafeFloorInline(admin.TabularInline):
    model = CafeFloor


class CafeImageInline(admin.TabularInline):
    model = CafeImage


@admin.register(Cafe)
class CafeAdmin(admin.GeoModelAdmin):
    list_display = ("id", "name", "floor_count", "is_opened", "district_city", "brand_name", "congestion_area_name", "address", "is_visible", "is_closed",)
    list_filter = ("is_visible", "is_opened", "is_closed", "brand__name", "district__city", "district__gu", "district__dong", "congestion_area__name")
    autocomplete_fields = ("district", "brand", "brand__name",)
    search_fields = ("name", "address",)
    ordering = ("is_visible", "-is_closed", "name",)
    inlines = (OpeningHourInline, CafeFloorInline, CafeImageInline,)
    list_select_related = ["district", "brand", "opening_hour"]
    save_as = True
    preserve_filters = True

    def floor_count(self, cafe): return len(cafe.cafe_floor.all())

    def district_city(self, cafe): return cafe.district.city if cafe.district else None

    def congestion_area_name(self, cafe):
        if cafe.congestion_area:
            areas = ""
            for area in cafe.congestion_area.all(): areas += f"{area.name}, "
            return areas
        else:
            return None

    def brand_name(self, cafe): return cafe.brand.name if cafe.brand else None
    
    def save_model(self, request, obj, form, change):
        obj.point = Point(obj.longitude, obj.latitude, srid=4326)
        obj.save()
        try:
            OpeningHoursUpdateAdmin.save_opening_hour(opening_hour_object=obj.opening_hour)
        except OpeningHour.DoesNotExist:
            pass

    floor_count.short_description = "층수"
    district_city.short_description = "구역"
    congestion_area_name.short_description = "혼잡도 지역"
    brand_name.short_description = "브랜드"


@admin.register(CafeImage)
class CafeImageAdmin(ImageModelAdmin):
    list_display = ("id", "cafe_name", "image_tag", "is_visible",)
    list_filter = ("is_visible",)
    autocomplete_fields = ("cafe__name",)
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
    list_filter = ("cafe__district__gu", "cafe__brand__name", "user__profile__nickname",)
    autocomplete_fields = ("user", "user__profile__nickname", "cafe__name")
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
    list_filter = ("cafe_floor__cafe__brand__name", "cafe_floor__cafe__district__city", "cafe_floor__cafe__district__gu", "cafe_floor__cafe__district__dong",)
    list_select_related = ["cafe_floor"]
    autocomplete_fields = ("cafe_floor__cafe__name",)
    date_hierarchy = "update"
    search_fields = ("cafe_floor__cafe__name",)
    ordering = ("-update",)
    save_as = True
    preserve_filters = True

    def cafe_name(self, prediction): return prediction.cafe_floor.cafe.name if prediction.cafe_floor else None

    cafe_name.short_description = "카페"


@admin.register(OccupancyRateUpdateLog)
class OccupancyRateUpdateLogAdmin(admin.ModelAdmin):
    list_display = ("id", "cafe_name_floor", "nickname", "occupancy_rate", "update", "is_google_map_prediction", "point", "congestion", "is_notified")
    list_filter = ("cafe_floor__cafe__brand__name", "cafe_floor__cafe__district__city", "cafe_floor__cafe__district__gu", "cafe_floor__cafe__district__dong", "is_google_map_prediction")
    autocomplete_fields = ("cafe_floor__cafe__name", "user", "user__profile__nickname",)
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
    autocomplete_fields = ("cafe_floor__cafe__name", "user", "user__profile__nickname",)
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

@admin.register(OpeningHour)
class OpeningHourAdmin(admin.ModelAdmin):
    list_display = ("id", "cafe_name", "mon", "tue", "wed", "thu", "fri", "sat", "sun")
    list_editable = ('mon', 'tue', "wed", "thu", "fri", "sat", "sun")
    autocomplete_fields = ("cafe__name",)
    search_fields = ("cafe__name",)
    ordering = ("mon",)
    save_as = True
    preserve_filters = True

    def cafe_name(self, obj): return obj.cafe.name if obj.cafe else None

    cafe_name.short_description = "카페"

    def save_model(self, request, obj, form, change):
        OpeningHoursUpdateAdmin.save_opening_hour(opening_hour_object=obj)
