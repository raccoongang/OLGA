# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-06-22 12:54
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('analytics', '0001_squashed_0004_auto_20170615_1451'),
    ]

    operations = [
        migrations.RenameField(
            model_name='edxinstallation',
            old_name='secret_token',
            new_name='access_token',
        ),
    ]
