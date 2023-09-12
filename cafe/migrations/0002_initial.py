# Generated by Django 4.2.1 on 2023-09-12 16:52

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('cafe', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='occupancyrateupdatelog',
            name='user',
            field=models.ForeignKey(blank=True, db_column='user', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='occupancy_rate_update_log', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='occupancyrateprediction',
            name='cafe_floor',
            field=models.OneToOneField(db_column='cafe_floor', on_delete=django.db.models.deletion.CASCADE, related_name='occupancy_rate_prediction', to='cafe.cafefloor'),
        ),
        migrations.AddField(
            model_name='dailyactivitystack',
            name='cafe_floor',
            field=models.ForeignKey(db_column='cafe_floor', on_delete=django.db.models.deletion.CASCADE, related_name='daily_activity_stack', to='cafe.cafefloor'),
        ),
        migrations.AddField(
            model_name='dailyactivitystack',
            name='user',
            field=models.ForeignKey(db_column='user', on_delete=django.db.models.deletion.CASCADE, related_name='daily_activity_stack', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddIndex(
            model_name='congestionarea',
            index=models.Index(fields=['south_west_latitude', 'south_west_longitude', 'north_east_latitude', 'north_east_longitude'], name='congestion_coordinate_index'),
        ),
        migrations.AddField(
            model_name='cafevip',
            name='cafe',
            field=models.ForeignKey(db_column='cafe', on_delete=django.db.models.deletion.CASCADE, related_name='cafe_vip', to='cafe.cafe'),
        ),
        migrations.AddField(
            model_name='cafevip',
            name='user',
            field=models.ForeignKey(db_column='user', on_delete=django.db.models.deletion.CASCADE, related_name='cafe_vip', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='cafetypetag',
            name='cafe',
            field=models.ForeignKey(db_column='cafe', on_delete=django.db.models.deletion.CASCADE, related_name='cafe_type_tag', to='cafe.cafe'),
        ),
        migrations.AddField(
            model_name='cafetypetag',
            name='user',
            field=models.ForeignKey(blank=True, db_column='user', default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='cafe_type_tag', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='cafeimage',
            name='cafe',
            field=models.ForeignKey(db_column='cafe', on_delete=django.db.models.deletion.CASCADE, related_name='cafe_image', to='cafe.cafe'),
        ),
        migrations.AddField(
            model_name='cafefloor',
            name='cafe',
            field=models.ForeignKey(db_column='cafe', on_delete=django.db.models.deletion.CASCADE, related_name='cafe_floor', to='cafe.cafe'),
        ),
        migrations.AddField(
            model_name='cafe',
            name='brand',
            field=models.ForeignKey(blank=True, db_column='brand', default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='cafe', to='cafe.brand'),
        ),
        migrations.AddField(
            model_name='cafe',
            name='congestion_area',
            field=models.ManyToManyField(blank=True, db_column='congestion_area', related_name='cafe', to='cafe.congestionarea'),
        ),
        migrations.AddField(
            model_name='cafe',
            name='district',
            field=models.ForeignKey(blank=True, db_column='district', default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='cafe', to='cafe.district'),
        ),
        migrations.AddIndex(
            model_name='cafe',
            index=models.Index(fields=['name'], name='cafe_name_index'),
        ),
        migrations.AddIndex(
            model_name='cafe',
            index=models.Index(fields=['address'], name='cafe_address_index'),
        ),
        migrations.AddIndex(
            model_name='cafe',
            index=models.Index(fields=['latitude', 'longitude'], name='cafe_coordinate_index'),
        ),
    ]
