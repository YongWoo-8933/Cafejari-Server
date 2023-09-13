# Generated by Django 4.2.1 on 2023-09-12 16:52

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('shop', '0001_initial'),
        ('cafe', '0002_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='usercoupon',
            name='user',
            field=models.ForeignKey(db_column='user', on_delete=django.db.models.deletion.CASCADE, related_name='user_coupon', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='item',
            name='brand',
            field=models.ForeignKey(blank=True, db_column='brand', default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='item', to='cafe.brand'),
        ),
        migrations.AddField(
            model_name='gifticon',
            name='item',
            field=models.ForeignKey(blank=True, db_column='item', default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='gifticon', to='shop.item'),
        ),
        migrations.AddField(
            model_name='gifticon',
            name='user',
            field=models.ForeignKey(blank=True, db_column='user', default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='gifticon', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddIndex(
            model_name='item',
            index=models.Index(fields=['name'], name='item_name_index'),
        ),
        migrations.AddIndex(
            model_name='item',
            index=models.Index(fields=['code'], name='item_code_index'),
        ),
        migrations.AddIndex(
            model_name='gifticon',
            index=models.Index(fields=['expiration_period'], name='gifticon_period_index'),
        ),
    ]