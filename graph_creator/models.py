from __future__ import unicode_literals

from django.db import models


class DataStorage(models.Model):
    courses_amount = models.IntegerField(default=0)
    students_amount = models.IntegerField(default=0)
    latitude = models.FloatField(default=0)
    longitude = models.FloatField(default=0)

