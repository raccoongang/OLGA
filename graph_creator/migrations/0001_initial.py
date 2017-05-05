# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-05-04 11:07
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DataStorage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('active_students_amount', models.IntegerField(default=0)),
                ('courses_amount', models.IntegerField(default=0)),
                ('latitude', models.FloatField(blank=True, default=0)),
                ('level', models.CharField(max_length=255)),
                ('longitude', models.FloatField(blank=True, default=0)),
                ('platform_name', models.CharField(blank=True, max_length=255, null=True)),
                ('platform_url', models.URLField(blank=True, null=True)),
                ('secret_token', models.CharField(max_length=255, null=True)),
                ('update', models.DateTimeField(default=datetime.datetime(2017, 5, 4, 11, 7, 23, 815313))),
            ],
        ),
    ]
