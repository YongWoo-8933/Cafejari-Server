# Generated by Django 4.2.1 on 2023-10-05 19:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cafe', '0007_alter_cafe_point'),
    ]

    operations = [
        migrations.AddField(
            model_name='location',
            name='is_visible',
            field=models.BooleanField(default=True),
        ),
    ]
