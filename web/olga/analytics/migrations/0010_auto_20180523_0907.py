# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2018-05-23 09:07
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('analytics', '0009_edxinstallation_uid'),
    ]

    operations = [
        migrations.AddField(
            model_name='installationstatistics',
            name='enthusiastic_students',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='installationstatistics',
            name='generated_certificates',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='installationstatistics',
            name='registered_students',
            field=models.IntegerField(default=0),
        ),
    ]
