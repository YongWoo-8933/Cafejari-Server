# Generated by Django 4.2.1 on 2023-10-05 11:10

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('notification', '0003_remove_pushnotification_user_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='pushnotification',
            name='user',
            field=models.ForeignKey(blank=True, db_column='user', default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='push_notification', to=settings.AUTH_USER_MODEL),
        ),
    ]
