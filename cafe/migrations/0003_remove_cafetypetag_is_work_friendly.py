# Generated by Django 4.2.1 on 2023-09-15 12:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cafe', '0002_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cafetypetag',
            name='is_work_friendly',
        ),
    ]
