# Generated by Django 4.2.1 on 2024-02-19 18:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0002_profile_cati_acidity_profile_cati_coffee_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='age_range',
            field=models.CharField(blank=True, choices=[('0~9', '0~9'), ('10~14', '10~14'), ('15~19', '15~19'), ('20~29', '20~29'), ('30~39', '30~39'), ('40~49', '40~49'), ('50~59', '50~59'), ('60~69', '60~69'), ('70~79', '70~79'), ('80~89', '80~89'), ('90~', '90~')], default=None, max_length=15, null=True),
        ),
    ]
