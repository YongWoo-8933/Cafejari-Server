import csv
import datetime
import logging
import os
import time
import urllib.parse
import uuid
import pytz
import requests

from threading import Thread
from django.contrib import admin
from django.contrib.gis.geos import Point

from django.core.files.base import ContentFile

from cafe.models import District, Brand, CongestionArea, Cafe, OpeningHour
from cafe.serializers import DistrictSerializer, BrandSerializer, CongestionAreaSerializer, CafeSerializer, \
    CafeFloorSerializer, OpeningHourSerializer, CafeImageSerializer
from cafejari.settings import LOCAL, MEDIA_ROOT, NAVER_GEO_KEY_ID, NAVER_GEO_KEY, GOOGLE_PLACE_API_KEY, TIME_ZONE
from cron.cafe_opening import update_cafe_opening
from cron.congestion import update_congestion_area
from cron.item import update_item_list
from cron.leaderboard import update_leaders
from cron.occupancy_prediction import predict_occupancy
from cron.occupancy_registration_challenge import check_occupancy_registration_challengers
from data.models import DistrictDataUpdate, ItemDataUpdate, CongestionDataUpdate, BrandDataUpdate, \
    CongestionAreaDataUpdate, NicknameAdjectiveDataUpdate, NicknameNounDataUpdate, CafeDataUpdate, CafePointUpdate, \
    OpeningHoursUpdate, OccupancyPredictionUpdate, CafeOpeningUpdate, LeaderUpdate, OccupancyRegistrationChallengeUpdate
from user.models import NicknameAdjective, NicknameNoun
from user.serializers import NicknameAdjectiveSerializer, NicknameNounSerializer
from utils import S3Manager


class CsvFileManageAdmin(admin.ModelAdmin):

    @staticmethod
    def get_opened_csv_file(file, encoding_type="UTF8"):
        if LOCAL:
            decoded_file_path = urllib.parse.unquote("/cafejari" + file.url)
            return open(decoded_file_path, "r", encoding=encoding_type)
        else:
            temp_file_path = f"{MEDIA_ROOT}/temp.csv"
            S3Manager.download_file(path=str(file), filename=temp_file_path)
            time.sleep(1)
            return open(temp_file_path, "r", encoding=encoding_type)


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
        Thread(target=update_item_list).start()


@admin.register(CongestionDataUpdate)
class CongestionUpdateAdmin(admin.ModelAdmin):
    list_display = ("id", "last_update",)
    date_hierarchy = "last_update"
    ordering = ("-last_update",)
    save_as = True
    preserve_filters = True

    def save_model(self, request, obj, form, change):
        obj.save()
        time.sleep(0.4)
        Thread(target=update_congestion_area).start()


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


@admin.register(CafeDataUpdate)
class CafeDataUpdateAdmin(CsvFileManageAdmin):
    list_display = ("id", "gu", "dong", "last_update",)
    date_hierarchy = "last_update"
    ordering = ("-last_update",)
    save_as = True
    preserve_filters = True

    def save_model(self, request, obj, form, change):
        obj.save()
        time.sleep(0.4)
        Thread(target=self.save_cafe_data, args=(obj,)).start()

    def save_cafe_data(self, obj):
        try:
            csv_file = self.get_opened_csv_file(file=obj.cafe_csv_file, encoding_type="CP949")
            reader = csv.reader(csv_file)

            # district 체크
            try:
                district_object = District.objects.get(gu=obj.gu, dong=obj.dong)
            except District.DoesNotExist:
                district_object = None

            for row in reader:
                cafe_name = row[1]
                opening_hour_raw_data = row[3] if row[3] else None
                road_address = row[4]
                total_floor = int(row[7])
                bottom_floor = int(row[8])
                no_seat_floor_list = row[9].split() if row[9] else []
                google_place_id = row[11] if row[11] else None

                # 좌표 얻어오기(못구하면 카페 패스)
                url = "https://naveropenapi.apigw.ntruss.com/map-geocode/v2/geocode"
                params = {
                    "query": road_address,
                    "X-NCP-APIGW-API-KEY-ID": NAVER_GEO_KEY_ID,
                    "X-NCP-APIGW-API-KEY": NAVER_GEO_KEY
                }
                try:
                    response = requests.get(url=url, params=params)
                    if response.status_code == 200:
                        addresses = response.json()['addresses']
                        if addresses:
                            latitude = float(addresses[0]['y'])
                            longitude = float(addresses[0]['x'])
                        else:
                            continue
                    else:
                        continue
                except requests.Timeout:
                    continue
                except requests.RequestException:
                    continue

                # congestion area 체크
                congestion_areas = CongestionArea.objects.filter(
                    south_west_latitude__lt=latitude,
                    south_west_longitude__lt=longitude,
                    north_east_latitude__gt=latitude,
                    north_east_longitude__gt=longitude
                )
                congestion_area_id_list = [congestion_area.id for congestion_area in congestion_areas]

                # brand 체크
                brand_object = None
                for brand in Brand.objects.all():
                    if brand.name in cafe_name:
                        brand_object = brand
                        break

                # 카페 data 생성
                cafe_data = {
                    "is_visible": True,
                    "name": cafe_name,
                    "address": road_address,
                    "latitude": latitude,
                    "longitude": longitude,
                    "point": Point(longitude, latitude, srid=4326),
                    "congestion_area": congestion_area_id_list,
                    "google_place_id": google_place_id,
                    "brand": brand_object.id if brand_object else None,
                    "district": district_object.id if district_object else None
                }

                # 중복되는 카페가 있는지 확인후 serializer 생성
                try:
                    Cafe.objects.get(name=cafe_name, address=road_address)
                    continue
                except Cafe.DoesNotExist:
                    cafe_serializer = CafeSerializer(data=cafe_data)

                # 카페 object 저장
                cafe_serializer.is_valid(raise_exception=True)
                new_cafe_object = cafe_serializer.save()

                # cafe floor 생성
                current_floor = bottom_floor
                for floor in range(total_floor):
                    if current_floor == 0: current_floor += 1
                    cafe_floor_serializer = CafeFloorSerializer(data={
                        "floor": current_floor,
                        "cafe": new_cafe_object.id,
                        "has_seat": str(current_floor) not in no_seat_floor_list
                    })
                    cafe_floor_serializer.is_valid(raise_exception=True)
                    cafe_floor_serializer.save()
                    current_floor += 1

                # opening hour 설정
                if opening_hour_raw_data:
                    opening_hour_line_list = opening_hour_raw_data.splitlines()
                    opening_hour_dict = {"월": "", "화": "", "수": "", "목": "", "금": "", "토": "", "일": ""}
                    for opening_hour_line in opening_hour_line_list:
                        # 시간에 해당하는 내용을 찾음
                        last_colon_index = opening_hour_line.rfind(": ")
                        if last_colon_index != -1:
                            time_string = opening_hour_line[last_colon_index + 2:]
                        else:
                            continue

                        # 요일 정보를 찾음
                        first_str = opening_hour_line[0]
                        if first_str == "매":
                            for key in opening_hour_dict: opening_hour_dict[key] = time_string
                        elif first_str in opening_hour_dict:
                            opening_hour_dict[first_str] = time_string

                    # openning hour dict의 유효성 확인
                    has_data = True
                    for key in opening_hour_dict:
                        if not opening_hour_dict[key]:
                            has_data = False
                            break

                    # 데이터 정리 및 저장
                    if has_data:
                        opening_hour_serializer = OpeningHourSerializer(data={
                            "mon": opening_hour_dict["월"],
                            "tue": opening_hour_dict["화"],
                            "wed": opening_hour_dict["수"],
                            "thu": opening_hour_dict["목"],
                            "fri": opening_hour_dict["금"],
                            "sat": opening_hour_dict["토"],
                            "sun": opening_hour_dict["일"],
                            "cafe": new_cafe_object.id
                        })
                        opening_hour_serializer.is_valid(raise_exception=True)
                        opening_hour_object = opening_hour_serializer.save()
                        OpeningHoursUpdateAdmin.save_opening_hour(opening_hour_object=opening_hour_object)
                        opening_hour_serializer.save()

                # cafe image 설정
                if google_place_id:
                    url = "https://maps.googleapis.com/maps/api/place/details/json"
                    params = {"place_id": google_place_id, "key": GOOGLE_PLACE_API_KEY}
                    references = []
                    try:
                        response = requests.get(url=url, params=params)
                        if response.status_code == 200:
                            result_json = response.json()
                            if 'result' in result_json and 'photos' in result_json['result']:
                                photo_raw_json_list = result_json['result']['photos']
                                references = [e['photo_reference'] for e in photo_raw_json_list]
                        else:
                            continue
                    except requests.Timeout:
                        continue
                    except requests.RequestException:
                        continue

                    url = "https://maps.googleapis.com/maps/api/place/photo"
                    for reference in references:
                        params = {
                            "key": GOOGLE_PLACE_API_KEY,
                            "photo_reference": reference,
                            "maxwidth": 1200,
                            "maxheight": 1200
                        }
                        try:
                            response = requests.get(url=url, params=params)
                            if response.status_code == 200:

                                temp_file_name = f"temp_{str(uuid.uuid1())}.jpeg"
                                with open(temp_file_name, 'wb') as file:
                                    for chunk in response.iter_content(1024):
                                        file.write(chunk)
                                time.sleep(0.4)
                                with open(temp_file_name, 'rb') as f:
                                    image = ContentFile(f.read(), name=temp_file_name)

                                cafe_image_serializer = CafeImageSerializer(data={
                                    "cafe": new_cafe_object.id,
                                    "image": image
                                })
                                cafe_image_serializer.is_valid(raise_exception=True)
                                cafe_image_serializer.save()
                                os.remove(temp_file_name)
                            else:
                                continue
                        except requests.Timeout:
                            continue
                        except requests.RequestException:
                            continue
        except Exception as e:
            logger = logging.getLogger('my')
            logger.error(e)



@admin.register(CafePointUpdate)
class CafePointUpdateAdmin(admin.ModelAdmin):
    list_display = ("id", "last_update",)
    date_hierarchy = "last_update"
    ordering = ("-last_update",)
    save_as = True
    preserve_filters = True

    def save_model(self, request, obj, form, change):
        obj.save()
        time.sleep(0.4)
        Thread(target=self.save_cafe_point).start()

    def save_cafe_point(self):
        cafe_queryset = Cafe.objects.all()
        for cafe_object in cafe_queryset:
            serializer = CafeSerializer(
                cafe_object,
                data={"point": Point(cafe_object.longitude, cafe_object.latitude, srid=4326)},
                partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()



@admin.register(OpeningHoursUpdate)
class OpeningHoursUpdateAdmin(admin.ModelAdmin):
    list_display = ("id", "last_update",)
    date_hierarchy = "last_update"
    ordering = ("-last_update",)
    save_as = True
    preserve_filters = True

    def save_model(self, request, obj, form, change):
        obj.save()
        time.sleep(0.4)
        Thread(target=self.save_opening_hours).start()

    @staticmethod
    def parse_hours(opening_hour_text):
        if "정보없음" in opening_hour_text:
            return None, None
        elif "휴무" in opening_hour_text:
            return datetime.time(2, 0, 0), datetime.time(2, 0, 10)
        else:
            try:
                opening_hour = int(opening_hour_text[:2])
                opening_minute = int(opening_hour_text[3:5])
                closing_hour = int(opening_hour_text[8:10])
                closing_minute = int(opening_hour_text[11:13])
                if closing_hour == 24:
                    closing_hour = 23
                    closing_minute = 59
                tz = pytz.timezone(TIME_ZONE)
                return datetime.time(opening_hour, opening_minute, 0, tzinfo=tz), datetime.time(closing_hour, closing_minute, 0, tzinfo=tz)
            except IndexError:
                logger = logging.getLogger('my')
                logger.error(f"IndexError: 문자열의 범위를 벗어났습니다. {opening_hour_text}")
                return None, None

    def save_opening_hours(self):
        opening_hour_queryset = OpeningHour.objects.all()
        for opening_hour_object in opening_hour_queryset:
            self.save_opening_hour(opening_hour_object=opening_hour_object)

    @staticmethod
    def save_opening_hour(opening_hour_object):
        data = {}
        if opening_hour_object.mon:
            data["mon_opening_time"], data["mon_closing_time"] = OpeningHoursUpdateAdmin.parse_hours(opening_hour_object.mon)
        if opening_hour_object.tue:
            data["tue_opening_time"], data["tue_closing_time"] = OpeningHoursUpdateAdmin.parse_hours(opening_hour_object.tue)
        if opening_hour_object.wed:
            data["wed_opening_time"], data["wed_closing_time"] = OpeningHoursUpdateAdmin.parse_hours(opening_hour_object.wed)
        if opening_hour_object.thu:
            data["thu_opening_time"], data["thu_closing_time"] = OpeningHoursUpdateAdmin.parse_hours(opening_hour_object.thu)
        if opening_hour_object.fri:
            data["fri_opening_time"], data["fri_closing_time"] = OpeningHoursUpdateAdmin.parse_hours(opening_hour_object.fri)
        if opening_hour_object.sat:
            data["sat_opening_time"], data["sat_closing_time"] = OpeningHoursUpdateAdmin.parse_hours(opening_hour_object.sat)
        if opening_hour_object.sun:
            data["sun_opening_time"], data["sun_closing_time"] = OpeningHoursUpdateAdmin.parse_hours(opening_hour_object.sun)

        serializer = OpeningHourSerializer(opening_hour_object, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()



@admin.register(CafeOpeningUpdate)
class CafeOpeningUpdateAdmin(admin.ModelAdmin):
    list_display = ("id", "last_update",)
    date_hierarchy = "last_update"
    ordering = ("-last_update",)
    save_as = True
    preserve_filters = True

    def save_model(self, request, obj, form, change):
        obj.save()
        time.sleep(0.4)
        Thread(target=update_cafe_opening).start()



@admin.register(OccupancyPredictionUpdate)
class OccupancyPredictionUpdateAdmin(admin.ModelAdmin):
    list_display = ("id", "last_update",)
    date_hierarchy = "last_update"
    ordering = ("-last_update",)
    save_as = True
    preserve_filters = True

    def save_model(self, request, obj, form, change):
        obj.save()
        time.sleep(0.4)
        Thread(target=predict_occupancy).start()



@admin.register(LeaderUpdate)
class LeaderUpdateAdmin(admin.ModelAdmin):
    list_display = ("id", "last_update",)
    date_hierarchy = "last_update"
    ordering = ("-last_update",)
    save_as = True
    preserve_filters = True

    def save_model(self, request, obj, form, change):
        obj.save()
        time.sleep(0.4)
        Thread(target=update_leaders).start()



@admin.register(OccupancyRegistrationChallengeUpdate)
class OccupancyRegistrationChallengeUpdateAdmin(admin.ModelAdmin):
    list_display = ("id", "last_update",)
    date_hierarchy = "last_update"
    ordering = ("-last_update",)
    save_as = True
    preserve_filters = True

    def save_model(self, request, obj, form, change):
        obj.save()
        time.sleep(0.4)
        Thread(target=check_occupancy_registration_challengers).start()
