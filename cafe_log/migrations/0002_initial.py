# Generated by Django 4.2.1 on 2023-09-12 16:52

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('cafe_log', '0001_initial'),
        ('cafe', '0002_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='cafelogreport',
            name='user',
            field=models.ForeignKey(db_column='user', on_delete=django.db.models.deletion.CASCADE, related_name='cafe_log_report', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='cafeloglike',
            name='cafe_log',
            field=models.ForeignKey(db_column='cafe_log', on_delete=django.db.models.deletion.CASCADE, related_name='like', to='cafe_log.cafelog'),
        ),
        migrations.AddField(
            model_name='cafeloglike',
            name='user',
            field=models.ForeignKey(db_column='user', on_delete=django.db.models.deletion.CASCADE, related_name='like', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='cafelog',
            name='cafe',
            field=models.ForeignKey(blank=True, db_column='cafe', default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='cafe_log', to='cafe.cafe'),
        ),
        migrations.AddField(
            model_name='cafelog',
            name='snapshot',
            field=models.ForeignKey(blank=True, db_column='snapshot', default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='cafe_log', to='cafe_log.snapshot'),
        ),
        migrations.AddField(
            model_name='cafelog',
            name='user',
            field=models.ForeignKey(blank=True, db_column='user', default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='cafe_log', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddIndex(
            model_name='cafelog',
            index=models.Index(fields=['created_at'], name='cafe_log_created_time_index'),
        ),
        migrations.AddIndex(
            model_name='cafelog',
            index=models.Index(fields=['updated_at'], name='cafe_log_updated_time_index'),
        ),
    ]