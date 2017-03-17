from __future__ import unicode_literals

from django.db import models


class DataStorage(models.Model):
    students_quantity = models.IntegerField(default=0)

