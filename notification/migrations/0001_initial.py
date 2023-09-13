# Generated by Django 4.2.1 on 2023-09-12 16:52

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='PushNotification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=31)),
                ('body', models.TextField()),
                ('pushed_at', models.DateTimeField(auto_now_add=True)),
                ('type', models.CharField(choices=[('공지', '공지'), ('활동', '활동'), ('이벤트', '이벤트'), ('마케팅', '마케팅'), ('기타', '기타')])),
            ],
            options={
                'db_table': 'notification_push_notification',
                'db_table_comment': '푸쉬 알림 모델',
                'ordering': ['-pushed_at'],
            },
        ),
    ]