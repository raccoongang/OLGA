# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-10-12 10:25
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('analytics', '0008_auto_20170814_1038'),
    ]

    operations = [
        migrations.AddField(
            model_name='edxinstallation',
            name='uid',
            field=models.CharField(max_length=255, null=True),
        ),
    ]
