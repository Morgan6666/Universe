# Generated by Django 3.2.10 on 2022-01-16 22:30

from django.db import migrations, models
import django.db.models.manager
import universeShops.app_account.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('phone', models.CharField(max_length=11, unique=True, validators=[universeShops.app_account.models.phone_validate])),
                ('name', models.CharField(max_length=150)),
                ('login', models.CharField(max_length=150)),
                ('is_active', models.BooleanField(default=True)),
                ('is_seller', models.BooleanField(default=False)),
                ('is_superuser', models.BooleanField(default=False)),
            ],
            options={
                'abstract': False,
            },
            managers=[
                ('object', django.db.models.manager.Manager()),
            ],
        ),
    ]
