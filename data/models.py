
from django.db import models


def district_csv_upload_path(instance, filename): return f"data/district/{filename}"


def brand_csv_upload_path(instance, filename): return f"data/brand/{filename}"


def congestion_area_csv_upload_path(instance, filename): return f"data/congestion_area/{filename}"


def nickname_adjective_csv_upload_path(instance, filename): return f"data/nickname_adjective/{filename}"


def nickname_noun_csv_upload_path(instance, filename): return f"data/nickname_noun/{filename}"


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
