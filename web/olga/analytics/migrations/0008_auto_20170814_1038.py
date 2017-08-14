# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-08-14 10:38
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('analytics', '0007_auto_20170801_1312'),
    ]

    operations = [
        migrations.AlterField(
            model_name='edxinstallation',
            name='latitude',
            field=models.FloatField(blank=True, help_text=b'Latitude coordinate of edX platform follows `float` type. Example: 50.10', null=True),
        ),
        migrations.AlterField(
            model_name='edxinstallation',
            name='longitude',
            field=models.FloatField(blank=True, help_text=b'Longitude coordinate of edX platform follows `float` type. Example: 40.05', null=True),
        ),
        migrations.AlterField(
            model_name='installationstatistics',
            name='students_per_country',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, default={}, help_text=b'This field has students country-count accordance. It follows `json` type. Example: {"RU": 2632, "CA": 18543, "UA": 2011, "null": 1}', null=True),
        ),
    ]
