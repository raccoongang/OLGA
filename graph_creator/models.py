"""
Models used to store and operate all data received from the edx platform.
"""

from __future__ import unicode_literals
from datetime import datetime

from django.db import models


class DataStorage(models.Model):
    """
    Model that stores data received from the edx-platform.
    """

    active_students_amount = models.IntegerField(default=0)
    courses_amount = models.IntegerField(default=0)
    last_data_update = models.DateTimeField(default=datetime.now())
    latitude = models.FloatField(default=0, blank=True)
    longitude = models.FloatField(default=0, blank=True)
    platform_name = models.CharField(max_length=255, null=True, blank=True)
    platform_url = models.URLField(null=True, blank=True)
    secret_token = models.CharField(max_length=255, null=True)
    statistics_level = models.CharField(max_length=255)
    students_per_country = models.TextField()
