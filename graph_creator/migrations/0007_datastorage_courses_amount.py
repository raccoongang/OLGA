# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-03-24 13:55
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('graph_creator', '0006_auto_20170323_1349'),
    ]

    operations = [
        migrations.AddField(
            model_name='datastorage',
            name='courses_amount',
            field=models.IntegerField(default=0),
        ),
    ]
