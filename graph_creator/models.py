"""
Models used to store and operate all data received from the edx platform.
"""

from __future__ import unicode_literals

from django.db import models


class DataStorage(models.Model):
    """
    Model that stores data received from the edx-platform.
    """

    courses_amount = models.IntegerField(default=0)
    students_amount = models.IntegerField(default=0)
    latitude = models.FloatField(default=0)
    longitude = models.FloatField(default=0)
    platform_url = models.URLField(null=True)
    secret_token = models.CharField(max_length=255, null=True)
