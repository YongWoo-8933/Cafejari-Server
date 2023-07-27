
import time

from django.contrib import admin
from cafe.models import District, Brand
from cafe.serializers import DistrictSerializer, BrandSerializer, CongestionAreaSerializer
from cron.congestion import update_congestion_area
from cron.item import update_item_list
from data.models import DistrictDataUpdate, ItemDataUpdate, CongestionDataUpdate, BrandDataUpdate, \
    CongestionAreaDataUpdate
from utils import S3Manager


@admin.register(DistrictDataUpdate)
class DistrictUpdateAdmin(admin.ModelAdmin):
    list_display = ("id", "last_update", "city", "gu_dong_csv_file",)
    list_filter = ("city",)
    date_hierarchy = "last_update"
    ordering = ("-last_update",)
    save_as = True
    preserve_filters = True

    def save_model(self, request, obj, form, change):
        obj.save()
        time.sleep(1)
        f = request.FILES.get("gu_dong_csv_file")
        reader = f.read().decode('utf-8').splitlines()
        response_dict = {}
        current_dong_list = []
        current_gu = ""
        for row in reader:
            if not any(row):
                response_dict[current_gu] = current_dong_list
                current_dong_list = []
                continue
            if row[1]:
                if row[0] == '번호':
                    continue
                else:
                    current_dong_list.append({"name": row[1], "latitude": float(row[3]), "longitude": float(row[4])})
            else:
                current_gu = row[0]
        response_dict[current_gu] = current_dong_list
        for gu in response_dict.keys():
            for dong_dict in response_dict[gu]:
                dong_name = dong_dict['name']
                latitude = dong_dict['latitude']
                longitude = dong_dict['longitude']
                try:
                    selected_district = District.objects.get(city=obj.city, gu=gu, dong=dong_name)
                    serializer = DistrictSerializer(
                        selected_district, data={"latitude": latitude, "longitude": longitude}, partial=True)
                except District.DoesNotExist:
                    serializer = DistrictSerializer(
                        data={"city": obj.city, "gu": gu, "dong": dong_name, "latitude": latitude,
                              "longitude": longitude})
                serializer.is_valid(raise_exception=True)
                serializer.save()
        S3Manager.delete_file(obj.gu_dong_csv_file)
        f.close()


@admin.register(CongestionAreaDataUpdate)
class CongestionAreaDataUpdateAdmin(admin.ModelAdmin):
    list_display = ("id", "last_update", "congestion_area_csv_file")
    date_hierarchy = "last_update"
    ordering = ("-last_update",)
    save_as = True
    preserve_filters = True

    def save_model(self, request, obj, form, change):
        obj.save()
        time.sleep(1)
        f = request.FILES.get("congestion_area_csv_file")
        reader = f.read().decode('utf-8').splitlines()
        for row in reader[1:]:
            if len(row) > 6:
                serializer = CongestionAreaSerializer(data={
                    "name": row[3],
                    "category": row[0],
                    "south_west_latitude": row[4],
                    "south_west_longitude": row[5],
                    "north_east_latitude": row[6],
                    "north_east_longitude": row[7]
                })
                serializer.is_valid(raise_exception=True)
                serializer.save()
        S3Manager.delete_file(obj.congestion_area_csv_file)
        f.close()


@admin.register(BrandDataUpdate)
class BrandDataUpdateAdmin(admin.ModelAdmin):
    list_display = ("id", "last_update", "brand_csv_file",)
    date_hierarchy = "last_update"
    ordering = ("-last_update",)
    save_as = True
    preserve_filters = True

    def save_model(self, request, obj, form, change):
        obj.save()
        time.sleep(1)
        f = request.FILES.get("brand_csv_file")
        reader = f.read().decode('utf-8').splitlines()
        brand_queryset = Brand.objects.all()
        brand_name_list = [obj.name for obj in brand_queryset]
        for row in reader:
            brand_name = row[0]
            if brand_name not in brand_name_list:
                serializer = BrandSerializer(data={"name": brand_name})
                serializer.is_valid(raise_exception=True)
                serializer.save()
        S3Manager.delete_file(obj.brand_csv_file)
        f.close()


@admin.register(ItemDataUpdate)
class ItemUpdateAdmin(admin.ModelAdmin):
    list_display = ("id", "last_update",)
    date_hierarchy = "last_update"
    ordering = ("-last_update",)
    save_as = True
    preserve_filters = True

    def save_model(self, request, obj, form, change):
        obj.save()
        update_item_list()


@admin.register(CongestionDataUpdate)
class CongestionUpdateAdmin(admin.ModelAdmin):
    list_display = ("id", "last_update",)
    date_hierarchy = "last_update"
    ordering = ("-last_update",)
    save_as = True
    preserve_filters = True

    def save_model(self, request, obj, form, change):
        obj.save()
        update_congestion_area()
