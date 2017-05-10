"""
Models used to store and operate all data received from the edx platform.
"""

from __future__ import unicode_literals
from datetime import datetime

from django.db import models
from django.conf import settings
from django.db.models import Sum, Count, Func, F, Value, functions



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

    @classmethod
    def timeline(cls):
        """
        Provide timeline in days for plotting on x axis.

        Future: add weeks, or month for dynamic range on plots.
        """
        timeline_datetimes =  cls.objects.order_by('last_data_update').values_list('last_data_update', flat=True).distinct()
        timeline_dates = [x.date().strftime('%Y-%m-%d')for x in timeline_datetimes]
        return timeline_dates

    @classmethod
    def data_per_period(cls):
        """
        Provide total students and courses from all services per period, day by default.

        We summarize values per day, because in same day we can receive data from multiple different instances.
        Same instance send data only once per day.

        Future: add weeks, month for dynamic range on plots.

        PostgreSQL: extra(select = {"month": '''DATE_TRUNC('month', creation_date)'''}) 
        SQlite3: extra(select={'date': 'django_date_trunc("day", "testapp_log"."datetime")'})

        It may be possible to do with Func, but it looks like there is no TRUNC in django, 
        and Substr is not working well with datetime objects.
        """        
        if settings.DEBUG: # sqlite3 specific
            datetime_to_days = {'date_in_days': 'django_date_trunc("day", "graph_creator_datastorage"."last_data_update")'}

        subquery = cls.objects.order_by('last_data_update').extra(datetime_to_days).values('date_in_days')

        students_per_day = subquery.annotate(students=Sum('active_students_amount')).values_list('students', flat=True)
        courses_per_day = subquery.annotate(courses=Sum('courses_amount')).values_list('courses', flat=True)
        # instances_per_day = subquery.annotate(instances=Count('secret_token')).values_list('instances', flat=True)   


        print list(students_per_day), list(courses_per_day)#, instances_per_day
        return list(students_per_day), list(courses_per_day)#, instances_per_day


