# Generated by Django 4.2.1 on 2023-09-12 16:52

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='MonthlyHotCafeLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(auto_now_add=True, unique=True)),
            ],
            options={
                'db_table': 'leaderboard_monthly_hot_cafe_log',
                'db_table_comment': '이달의 카페로그',
                'ordering': ['-date'],
            },
        ),
        migrations.CreateModel(
            name='MonthSharingRanker',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sharing_count', models.IntegerField()),
            ],
            options={
                'db_table': 'leaderboard_month_sharing_ranker',
                'db_table_comment': '월간 공유 활동 랭커',
                'ordering': ['-sharing_count'],
            },
        ),
        migrations.CreateModel(
            name='TotalSharingRanker',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sharing_count', models.IntegerField()),
            ],
            options={
                'db_table': 'leaderboard_total_sharing_ranker',
                'db_table_comment': '누적 공유 활동 랭커',
                'ordering': ['-sharing_count'],
            },
        ),
        migrations.CreateModel(
            name='WeekSharingRanker',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sharing_count', models.IntegerField()),
            ],
            options={
                'db_table': 'leaderboard_week_sharing_ranker',
                'db_table_comment': '주간 공유 활동 랭커',
                'ordering': ['-sharing_count'],
            },
        ),
    ]