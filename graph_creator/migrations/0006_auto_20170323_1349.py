# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-03-23 13:49
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('graph_creator', '0005_auto_20170316_1843'),
    ]

    operations = [
        migrations.RenameField(
            model_name='datastorage',
            old_name='students_quantity',
            new_name='students_amount',
        ),
        migrations.AddField(
            model_name='datastorage',
            name='latitude',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='datastorage',
            name='longitude',
            field=models.FloatField(default=0),
        ),
    ]
