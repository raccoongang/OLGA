"""
Models used to store and operate all data received from the edx platform.
"""

from __future__ import unicode_literals
from datetime import datetime, timedelta
import json

from django.db import models
from django.db.models import Sum, Count, DateField
from django.db.models.functions import Trunc


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
        timeline_datetimes =  cls.objects.order_by(
            'last_data_update'
        ).values_list('last_data_update', flat=True).distinct()

        timeline_dates = [x.date().strftime('%Y-%m-%d') for x in timeline_datetimes]
        return timeline_dates

    @classmethod
    def data_per_period(cls):
        """
        Provide total students, courses and instances, from all services per period, day by default.

        We summarize values per day, because in same day we can receive data from multiple different instances.
        We suppose, that every instance send data only once per day.

        Future: add weeks, month for dynamic range on plots.

        PostgreSQL: extra(select = {"month": '''DATE_TRUNC('month', creation_date)'''}) 
        SQlite3: extra(select={'date': 'django_date_trunc("day", "testapp_log"."datetime")'})
        """

        subquery = cls.objects.order_by('last_data_update').annotate(
            date_in_days=Trunc('last_data_update', 'day', output_field=DateField())
        ).values('date_in_days')

        students_per_day = subquery.annotate(students=Sum('active_students_amount')).values_list('students', flat=True)
        courses_per_day = subquery.annotate(courses=Sum('courses_amount')).values_list('courses', flat=True)
        instances_per_day = subquery.annotate(instances=Count('secret_token')).values_list('instances', flat=True)

        return list(students_per_day), list(courses_per_day), list(instances_per_day)

    @classmethod
    def overall_counts(cls):
        """
        Provide total count of all instances, courses and students from all services per period, day by default.
        """

        all_unique_instances = DataStorage.objects.filter(
            last_data_update__lt=datetime.today(), last_data_update__gt=datetime.today() - timedelta(days=1)
        )

        instances_count = all_unique_instances.count()
        courses_count = all_unique_instances.aggregate(Sum('courses_amount'))['courses_amount__sum']
        students_count = all_unique_instances.aggregate(Sum('active_students_amount'))['active_students_amount__sum']

        return instances_count, courses_count, students_count

    @classmethod
    def worlds_students_per_country_statistics(cls):
        students_per_country_unicodes = list(cls.objects.values_list('students_per_country', flat=True))
        students_per_country_dicts = [json.loads(
            students_per_country_unicodes[instance]) for instance in range(len(students_per_country_unicodes)-1)
        ]

        world_students_per_country = {}

        for instance in students_per_country_dicts:
            for country, count in instance.iteritems():
                if country in world_students_per_country:
                    world_students_per_country[country] += count
                else:
                    world_students_per_country[country] = count

        return world_students_per_country
