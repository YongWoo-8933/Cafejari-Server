from django.db import models


class Version(models.Model):
    major = models.IntegerField()
    minor = models.IntegerField()
    patch = models.IntegerField()
    updated_at = models.DateTimeField(auto_now_add=True)
    description = models.TextField()

    class Meta:
        db_table = 'app_config_version'
        db_table_comment = '앱 버전 구분 모델'
        app_label = 'app_config'
        ordering = ['-updated_at']
