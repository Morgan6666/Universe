# Generated by Django 3.2.10 on 2022-01-08 12:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0002_auto_20220106_1730'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='universeethnicanalitics',
            name='universe',
        ),
        migrations.DeleteModel(
            name='UniverseDemographicAnalitics',
        ),
        migrations.DeleteModel(
            name='UniverseEthnicAnalitics',
        ),
    ]