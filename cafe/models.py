
from enum import Enum

from django.db import models


class District(models.Model):
    city = models.CharField(max_length=15)
    gu = models.CharField(max_length=15)
    dong = models.CharField(max_length=15, null=True, blank=True, default=None)
    latitude = models.FloatField()
    longitude = models.FloatField()

    class Meta:
        db_table = 'cafe_district'
        db_table_comment = '지역 구분 모델, oo시 oo구 까지'
        app_label = 'cafe'
        ordering = ['city', 'gu', 'dong']


class Congestion(Enum):
    Zero = '여유'
    One = '보통'
    Two = '약간 붐빔'
    Three = '붐빔'


class CongestionArea(models.Model):
    name = models.CharField(max_length=31, unique=True)
    category = models.CharField(max_length=15)
    current_congestion = models.CharField(
        default=Congestion.Zero.value,
        choices=((congestion.value, congestion.value) for congestion in Congestion)
    )
    south_west_latitude = models.FloatField()
    south_west_longitude = models.FloatField()
    north_east_latitude = models.FloatField()
    north_east_longitude = models.FloatField()

    class Meta:
        db_table = 'cafe_congestion_area'
        db_table_comment = '혼잡도 정보 제공받는 지역'
        app_label = 'cafe'
        ordering = ['category', 'name',]
        indexes = [
            models.Index(
                fields=["south_west_latitude", "south_west_longitude", "north_east_latitude", "north_east_longitude"],
                name="congestion_coordinate_index"
            ),
        ]


def brand_image_upload_path(instance, filename): return f"cafe/brand/{instance.name}_로고_{filename}"


class Brand(models.Model):
    name = models.CharField(max_length=31, unique=True)
    image = models.ImageField(upload_to=brand_image_upload_path, default=None, blank=True, null=True)
    has_item = models.BooleanField(default=False)

    class Meta:
        db_table = 'cafe_brand'
        db_table_comment = '카페의 브랜드 구분 모델'
        app_label = 'cafe'
        ordering = ['name']


def tag_image_upload_path(instance, filename):
    return f"cafe/tag/{instance.name}_태그_{filename}"


class CafeTypeTag(models.Model):
    has_openness = models.BooleanField()
    is_coffee_focused = models.BooleanField()
    is_work_friendly = models.BooleanField()
    user = models.ForeignKey(
        'user.User',
        on_delete=models.SET_NULL,
        related_name="cafe_type_tag",
        db_column="user",
        default=None,
        blank=True,
        null=True
    )
    cafe = models.ForeignKey(
        'Cafe',
        on_delete=models.CASCADE,
        related_name="cafe_type_tag",
        db_column="cafe"
    )

    class Meta:
        db_table = 'cafe_cafe_type_tag'
        db_table_comment = 'CATI 구분을 위한 type tag 모델'
        app_label = 'cafe'
        ordering = ['cafe__name']


class Cafe(models.Model):
    is_visible = models.BooleanField(default=True)
    is_closed = models.BooleanField(default=False)
    name = models.CharField(max_length=63)
    address = models.CharField(max_length=63)
    latitude = models.FloatField()
    longitude = models.FloatField()
    district = models.ForeignKey(
        'District',
        on_delete=models.SET_NULL,
        related_name="cafe",
        db_column="district",
        default=None,
        blank=True,
        null=True
    )
    congestion_area = models.ManyToManyField(
        'CongestionArea',
        related_name="cafe",
        db_column="congestion_area",
        blank=True,
    )
    brand = models.ForeignKey(
        'Brand',
        on_delete=models.SET_NULL,
        related_name="cafe",
        db_column="brand",
        default=None,
        blank=True,
        null=True
    )

    class Meta:
        db_table = 'cafe_cafe'
        db_table_comment = '카페 모델'
        app_label = 'cafe'
        ordering = ['name']
        indexes = [
            models.Index(fields=["name"], name="cafe_name_index"),
            models.Index(fields=["address"], name="cafe_address_index"),
            models.Index(fields=["latitude", "longitude"], name="cafe_coordinate_index"),
        ]


def cafe_image_upload_path(instance, filename):
    return f"cafe/cafe_image/{instance.cafe.name}_{filename}"


class CafeImage(models.Model):
    is_visible = models.BooleanField(default=True)
    image = models.ImageField(upload_to=cafe_image_upload_path)
    cafe = models.ForeignKey(
        'Cafe',
        on_delete=models.CASCADE,
        related_name="cafe_image",
        db_column="cafe"
    )

    class Meta:
        db_table = 'cafe_cafe_image'
        db_table_comment = '카페 사진 모델'
        app_label = 'cafe'
        ordering = ["cafe__name"]


class OpeningHour(models.Model):
    mon = models.CharField(max_length=31)
    tue = models.CharField(max_length=31)
    wed = models.CharField(max_length=31)
    thu = models.CharField(max_length=31)
    fri = models.CharField(max_length=31)
    sat = models.CharField(max_length=31)
    sun = models.CharField(max_length=31)
    cafe = models.OneToOneField(
        'Cafe',
        on_delete=models.CASCADE,
        related_name="opening_hour",
        db_column="cafe"
    )

    class Meta:
        db_table = 'cafe_opening_hour'
        db_table_comment = '카페 영업 시간 모델'
        app_label = 'cafe'
        ordering = ["cafe__name"]


class CafeFloor(models.Model):
    floor = models.IntegerField(default=1)  # 1층을 1로 표시
    has_seat = models.BooleanField(default=True)
    wall_socket_rate = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True, default=None)
    restroom = models.CharField(max_length=31, null=True, blank=True, default=None)
    cafe = models.ForeignKey(
        'Cafe',
        on_delete=models.CASCADE,
        related_name="cafe_floor",
        db_column="cafe"
    )

    class Meta:
        db_table = 'cafe_cafe_floor'
        db_table_comment = '카페 각 층 모델'
        app_label = 'cafe'
        ordering = ["cafe__name"]


class CafeVIP(models.Model):
    update_count = models.IntegerField()
    cafe = models.ForeignKey(
        'Cafe',
        on_delete=models.CASCADE,
        related_name="cafe_vip",
        db_column="cafe"
    )
    user = models.ForeignKey(
        'user.User',
        on_delete=models.CASCADE,
        related_name="cafe_vip",
        db_column="user"
    )

    class Meta:
        db_table = 'cafe_cafe_vip'
        db_table_comment = '각 카페의 vip'
        app_label = 'cafe'
        ordering = ["-update_count"]


class OccupancyRatePrediction(models.Model):
    occupancy_rate = models.DecimalField(max_digits=3, decimal_places=2)
    update = models.DateTimeField(auto_now_add=True)
    cafe_floor = models.OneToOneField(
        "CafeFloor",
        on_delete=models.CASCADE,
        related_name="occupancy_rate_prediction",
        db_column="cafe_floor"
    )

    class Meta:
        db_table = 'cafe_occupancy_rate_prediction'
        db_table_comment = '카페 층별 좌석 점유율 예측값'
        app_label = 'cafe'
        ordering = ["update", "occupancy_rate"]


class OccupancyRateUpdateLog(models.Model):
    occupancy_rate = models.DecimalField(max_digits=3, decimal_places=2)
    update = models.DateTimeField(auto_now_add=True)
    point = models.IntegerField(default=0)
    is_notified = models.BooleanField(default=False)
    cafe_floor = models.ForeignKey(
        'CafeFloor',
        on_delete=models.SET_NULL,
        related_name="occupancy_rate_update_log",
        db_column="cafe_floor",
        blank=True,
        null=True
    )
    user = models.ForeignKey(
        'user.User',
        on_delete=models.SET_NULL,
        related_name="occupancy_rate_update_log",
        db_column="user",
        blank=True,
        null=True
    )

    class Meta:
        db_table = 'cafe_occupancy_rate_update_log'
        db_table_comment = '좌석 점유율 업데이트 로그'
        app_label = 'cafe'
        ordering = ["-update"]


class DailyActivityStack(models.Model):
    update = models.DateTimeField(auto_now_add=True, db_index=True)
    cafe_floor = models.ForeignKey(
        'CafeFloor',
        on_delete=models.CASCADE,
        related_name="daily_activity_stack",
        db_column="cafe_floor"
    )
    user = models.ForeignKey(
        'user.User',
        on_delete=models.CASCADE,
        related_name="daily_activity_stack",
        db_column="user"
    )

    class Meta:
        db_table = 'cafe_daily_activity_stack'
        db_table_comment = '당일 혼잡도 공유 활동 스택'
        app_label = 'cafe'
        ordering = ["-update"]
