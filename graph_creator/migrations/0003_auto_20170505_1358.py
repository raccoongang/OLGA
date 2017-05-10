# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-05-05 13:58
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('graph_creator', '0002_auto_20170504_1339'),
    ]

    operations = [
        migrations.RenameField(
            model_name='datastorage',
            old_name='level',
            new_name='statistics_level',
        ),
        migrations.RemoveField(
            model_name='datastorage',
            name='update',
        ),
        migrations.AddField(
            model_name='datastorage',
            name='last_data_update',
            field=models.DateTimeField(default=datetime.datetime(2017, 5, 5, 13, 58, 42, 85730)),
        ),
    ]