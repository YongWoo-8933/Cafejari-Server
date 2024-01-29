# Generated by Django 4.2.1 on 2024-01-12 19:12

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('request', '0004_remove_cafeinformationsuggestion_is_open_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='AppFeedback',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time', models.DateTimeField(auto_now_add=True)),
                ('reason', models.BooleanField(default=False)),
                ('user', models.ForeignKey(blank=True, db_column='user', default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='app_feedback', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'app_feedback',
                'db_table_comment': '앱 사용 피드백 제출',
                'ordering': ['-time'],
            },
        ),
    ]
