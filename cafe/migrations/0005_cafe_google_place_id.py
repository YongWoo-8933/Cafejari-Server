# Generated by Django 4.2.1 on 2023-09-20 13:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cafe', '0004_cati_delete_cafetypetag'),
    ]

    operations = [
        migrations.AddField(
            model_name='cafe',
            name='google_place_id',
            field=models.CharField(blank=True, default=None, max_length=255, null=True),
        ),
    ]
