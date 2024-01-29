from django.contrib.gis.db import models


class AdLog(models.Model):
    name = models.CharField(max_length=15)
    description = models.TextField()
    date = models.DateField(auto_now_add=True)
    count = models.IntegerField()

    class Meta:
        db_table = 'ad_ad_log'
        db_table_comment = '광고 로그 모델(일별 구분)'
        app_label = 'ad'
        ordering = ['-date', 'name']
