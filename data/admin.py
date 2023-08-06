import csv
import time

from django.contrib import admin
from cafe.models import District, Brand, CongestionArea
from cafe.serializers import DistrictSerializer, BrandSerializer, CongestionAreaSerializer
from cafejari.settings import LOCAL, MEDIA_ROOT, BASE_DIR, AWS_S3_DOMAIN
from cron.congestion import update_congestion_area
from cron.item import update_item_list
from data.models import DistrictDataUpdate, ItemDataUpdate, CongestionDataUpdate, BrandDataUpdate, \
    CongestionAreaDataUpdate, NicknameAdjectiveDataUpdate, NicknameNounDataUpdate
from user.models import NicknameAdjective, NicknameNoun
from user.serializers import NicknameAdjectiveSerializer, NicknameNounSerializer
from utils import S3Manager


class CsvFileManageAdmin(admin.ModelAdmin):

    @staticmethod
    def get_opened_csv_file(file):
        if LOCAL:
            path = f"{BASE_DIR}/{file.url}"
            return open(path, "r", encoding="utf-8-sig")
        else:
            temp_file_path = f"{MEDIA_ROOT}/temp.csv"
            S3Manager.download_file(path=str(file), filename=temp_file_path)
            time.sleep(1)
            return open(temp_file_path, "r", encoding="utf-8-sig")


@admin.register(DistrictDataUpdate)
class DistrictUpdateAdmin(CsvFileManageAdmin):
    list_display = ("id", "last_update", "city", "gu_dong_csv_file",)
    list_filter = ("city",)
    date_hierarchy = "last_update"
    ordering = ("-last_update",)
    save_as = True
    preserve_filters = True

    def save_model(self, request, obj, form, change):
        obj.save()
        time.sleep(0.2)
        f = self.get_opened_csv_file(file=obj.gu_dong_csv_file)
        reader = csv.reader(f)
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
                    current_dong_list.append({"name": row[1].strip(), "latitude": float(row[3].strip()), "longitude": float(row[4].strip())})
            else:
                current_gu = row[0].strip()
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
        f.close()


@admin.register(CongestionAreaDataUpdate)
class CongestionAreaDataUpdateAdmin(CsvFileManageAdmin):
    list_display = ("id", "last_update", "congestion_area_csv_file")
    date_hierarchy = "last_update"
    ordering = ("-last_update",)
    save_as = True
    preserve_filters = True

    def save_model(self, request, obj, form, change):
        obj.save()
        time.sleep(0.5)
        f = self.get_opened_csv_file(file=obj.congestion_area_csv_file)
        reader = csv.reader(f)
        areas = CongestionArea.objects.all()
        area_name_list = [area.name for area in areas]
        first = True
        for row in reader:
            if first:
                first = False
                continue
            if len(row) > 6:
                name = row[3].strip()
                if name in area_name_list:
                    obj = CongestionArea.objects.get(name=name)
                    serializer = CongestionAreaSerializer(obj, data={
                        "category": row[0],
                        "south_west_latitude": row[4],
                        "south_west_longitude": row[5],
                        "north_east_latitude": row[6],
                        "north_east_longitude": row[7]
                    }, partial=True)
                else:
                    serializer = CongestionAreaSerializer(data={
                        "name": name,
                        "category": row[0],
                        "south_west_latitude": row[4],
                        "south_west_longitude": row[5],
                        "north_east_latitude": row[6],
                        "north_east_longitude": row[7]
                    })
                serializer.is_valid(raise_exception=True)
                serializer.save()
        f.close()


@admin.register(BrandDataUpdate)
class BrandDataUpdateAdmin(CsvFileManageAdmin):
    list_display = ("id", "last_update", "brand_csv_file",)
    date_hierarchy = "last_update"
    ordering = ("-last_update",)
    save_as = True
    preserve_filters = True

    def save_model(self, request, obj, form, change):
        obj.save()
        time.sleep(0.5)
        f = self.get_opened_csv_file(file=obj.brand_csv_file)
        reader = csv.reader(f)
        brand_name_list = [obj.name for obj in Brand.objects.all()]
        for row in reader:
            brand_name = row[0].strip()
            if brand_name not in brand_name_list:
                serializer = BrandSerializer(data={"name": brand_name})
                serializer.is_valid(raise_exception=True)
                serializer.save()
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


@admin.register(NicknameAdjectiveDataUpdate)
class NicknameAdjectiveDataUpdateAdmin(CsvFileManageAdmin):
    list_display = ("id", "last_update",)
    date_hierarchy = "last_update"
    ordering = ("-last_update",)
    save_as = True
    preserve_filters = True

    def save_model(self, request, obj, form, change):
        obj.save()
        time.sleep(0.5)
        f = self.get_opened_csv_file(file=obj.adjective_csv_file)
        reader = csv.reader(f)
        adjective_queryset = NicknameAdjective.objects.all()
        filter_set = set()
        for row in reader:
            adjective = row[0].strip()
            if adjective not in filter_set:
                filter_set.add(adjective)
                try:
                    adjective_object = adjective_queryset.get(value=adjective)
                    serializer = NicknameAdjectiveSerializer(adjective_object,
                                                             data={"value": adjective, "length": len(adjective)},
                                                             partial=True)
                except NicknameAdjective.DoesNotExist:
                    serializer = NicknameAdjectiveSerializer(data={"value": adjective, "length": len(adjective)})
                serializer.is_valid(raise_exception=True)
                serializer.save()
        f.close()


@admin.register(NicknameNounDataUpdate)
class NicknameNounDataUpdateAdmin(CsvFileManageAdmin):
    list_display = ("id", "last_update",)
    date_hierarchy = "last_update"
    ordering = ("-last_update",)
    save_as = True
    preserve_filters = True

    def save_model(self, request, obj, form, change):
        obj.save()
        time.sleep(0.5)
        f = self.get_opened_csv_file(file=obj.noun_csv_file)
        reader = csv.reader(f)
        noun_queryset = NicknameNoun.objects.all()
        filter_set = set()
        for row in reader:
            noun_type = row[0].strip()
            noun = row[1].strip()
            if noun not in filter_set:
                filter_set.add(noun)
                try:
                    noun_object = noun_queryset.get(type=noun_type, value=noun)
                    serializer = NicknameNounSerializer(noun_object,
                                                        data={"value": noun, "type": noun_type},
                                                        partial=True)
                except NicknameNoun.DoesNotExist:
                    serializer = NicknameNounSerializer(data={"value": noun, "type": noun_type})
                serializer.is_valid(raise_exception=True)
                serializer.save()
        f.close()
