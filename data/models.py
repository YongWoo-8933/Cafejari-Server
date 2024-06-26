
from django.db import models


def district_csv_upload_path(instance, filename): return f"data/district/{filename}"


def brand_csv_upload_path(instance, filename): return f"data/brand/{filename}"


def congestion_area_csv_upload_path(instance, filename): return f"data/congestion_area/{filename}"


def nickname_adjective_csv_upload_path(instance, filename): return f"data/nickname_adjective/{filename}"


def nickname_noun_csv_upload_path(instance, filename): return f"data/nickname_noun/{filename}"


def cafe_csv_upload_path(instance, filename): return f"data/cafe/{filename}"


class DistrictDataUpdate(models.Model):
    last_update = models.DateTimeField(auto_now_add=True)
    city = models.CharField(max_length=15)
    gu_dong_csv_file = models.FileField(upload_to=district_csv_upload_path)

    class Meta:
        db_table = 'data_district_data_update'
        db_table_comment = '지역정보 업데이트하는 admin전용 모델'
        app_label = 'data'
        ordering = ['-last_update', 'city']


class BrandDataUpdate(models.Model):
    last_update = models.DateTimeField(auto_now_add=True)
    brand_csv_file = models.FileField(upload_to=brand_csv_upload_path)

    class Meta:
        db_table = 'data_brand_data_update'
        db_table_comment = '브랜드정보 업데이트하는 admin전용 모델'
        app_label = 'data'
        ordering = ['-last_update']


class ItemDataUpdate(models.Model):
    last_update = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'data_item_data_update'
        db_table_comment = '아이템, 브랜드 업데이트하는 admin전용 모델'
        app_label = 'data'
        ordering = ['-last_update']


class CongestionDataUpdate(models.Model):
    last_update = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'data_congestion_data_update'
        db_table_comment = '지역 실시간 혼잡도 업데이트하는 admin전용 모델'
        app_label = 'data'
        ordering = ['-last_update']


class CongestionAreaDataUpdate(models.Model):
    last_update = models.DateTimeField(auto_now_add=True)
    congestion_area_csv_file = models.FileField(upload_to=congestion_area_csv_upload_path)

    class Meta:
        db_table = 'data_congestion_area_data_update'
        db_table_comment = '혼잡도 제공 해주는 지역 정보 업데이트하는 admin전용 모델'
        app_label = 'data'
        ordering = ['-last_update']


class NicknameAdjectiveDataUpdate(models.Model):
    last_update = models.DateTimeField(auto_now_add=True)
    adjective_csv_file = models.FileField(upload_to=nickname_adjective_csv_upload_path)

    class Meta:
        db_table = 'data_nickname_adjective_data_update'
        db_table_comment = '닉네임 자동생성 후보 형용사 업데이트'
        app_label = 'data'
        ordering = ['-last_update']


class NicknameNounDataUpdate(models.Model):
    last_update = models.DateTimeField(auto_now_add=True)
    noun_csv_file = models.FileField(upload_to=nickname_noun_csv_upload_path)

    class Meta:
        db_table = 'data_nickname_noun_data_update'
        db_table_comment = '닉네임 자동생성 후보 명사 업데이트'
        app_label = 'data'
        ordering = ['-last_update']


class CafeDataUpdate(models.Model):
    gu = models.CharField(max_length=15)
    dong = models.CharField(max_length=15)
    last_update = models.DateTimeField(auto_now_add=True)
    cafe_csv_file = models.FileField(upload_to=cafe_csv_upload_path)

    class Meta:
        db_table = 'data_cafe_data_update'
        db_table_comment = '새로운 카페를 추가하고 정보 업데이트'
        app_label = 'data'
        ordering = ['-last_update']


class CafePointUpdate(models.Model):
    last_update = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'data_cafe_point_update'
        db_table_comment = '각 카페의 좌표에 따라 point값 지정'
        app_label = 'data'
        ordering = ['-last_update']


class OpeningHoursUpdate(models.Model):
    last_update = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'data_opening_hours_update'
        db_table_comment = '카페 영업시간 정보의 string으로부터 time을 추출해 저장'
        app_label = 'data'
        ordering = ['-last_update']


class CafeOpeningUpdate(models.Model):
    last_update = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'data_cafe_opening_update'
        db_table_comment = '카페 영업시간 정보에 따라 영업중인지 여부 업데이트'
        app_label = 'data'
        ordering = ['-last_update']


class OccupancyPredictionUpdate(models.Model):
    last_update = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'data_occupancy_prediction_update'
        db_table_comment = '카페 예상 혼잡도 저장'
        app_label = 'data'
        ordering = ['-last_update']


class OccupancyRegistrationChallengeUpdate(models.Model):
    last_update = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'data_occupancy_registration_challenge_update'
        db_table_comment = '혼잡도 등록 챌린지 정산'
        app_label = 'data'
        ordering = ['-last_update']


class LeaderUpdate(models.Model):
    last_update = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'data_leader_update'
        db_table_comment = '랭킹정보 업데이트'
        app_label = 'data'
        ordering = ['-last_update']
