"""
Models used to store and operate all data received from the edx platform.
"""

from __future__ import unicode_literals
from collections import defaultdict
import datetime
import json

from django.db import models
from django.db.models import Sum, Count, DateField
from django.db.models.functions import Trunc


def get_previous_day_start_and_end_dates():  # pylint: disable=invalid-name
    """
    Get accurate start and end dates, that create segment between them equal to a full last calendar day.

    Returns:
        start_of_day (date): Previous day`s start. Example for 2017-05-15 is 2017-05-15.
        end_of_day (date): Previous day`s end, it`s a next day (tomorrow) toward day`s start,
                           that doesn't count in segment. Example for 2017-05-15 is 2017-05-16.
    """

    end_of_day = datetime.date.today()
    start_of_day = end_of_day - datetime.timedelta(days=1)

    return start_of_day, end_of_day


class DataStorage(models.Model):
    """
    Model that stores data received from the edx-platform.
    """

    active_students_amount_day = models.IntegerField(default=0)
    active_students_amount_week = models.IntegerField(default=0)
    active_students_amount_month = models.IntegerField(default=0)
    courses_amount = models.IntegerField(default=0)
    data_update = models.DateTimeField(default=datetime.datetime.now())
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

        timeline_datetimes = cls.objects.order_by('data_update').values_list('data_update', flat=True).distinct()
        timeline_dates = [x.date().strftime('%Y-%m-%d') for x in timeline_datetimes]

        return timeline_dates

    @classmethod
    def data_per_period(cls):
        """
        Provide total students, courses and instances, from all services per period, day by default.

        We summarize values per day, because in same day we can receive data from multiple different instances.
        We suppose, that every instance send data only once per day.

        Future: add weeks, month for dynamic range on plots.
        """

        subquery = cls.objects.annotate(
            date_in_days=Trunc('data_update', 'day', output_field=DateField())
        ).values('date_in_days').order_by()

        # last order_by() is needed:
        # http://chase-seibert.github.io/blog/2012/02/24/django-aggregation-group-by-day.html
        # https://docs.djangoproject.com/en/dev/topics/db/aggregation/#interaction-with-default-ordering-or-order-by

        students_per_day = subquery.annotate(
            students=Sum('active_students_amount_day')
        ).values_list('students', flat=True)

        courses_per_day = subquery.annotate(courses=Sum('courses_amount')).values_list('courses', flat=True)
        instances_per_day = subquery.annotate(instances=Count('secret_token')).values_list('instances', flat=True)

        return list(students_per_day), list(courses_per_day), list(instances_per_day)

    @classmethod
    def overall_counts(cls):
        """
        Provide total count of all instances, courses and students from all instances per previous calendar day.
        """

        start_of_day, end_of_day = get_previous_day_start_and_end_dates()

        all_unique_instances = DataStorage.objects.filter(data_update__gte=start_of_day, data_update__lt=end_of_day)

        instances_count = all_unique_instances.count()
        courses_count = all_unique_instances.aggregate(Sum('courses_amount'))['courses_amount__sum']
        students_count = all_unique_instances.aggregate(
            Sum('active_students_amount_day'))['active_students_amount_day__sum']

        return instances_count, courses_count, students_count

    @classmethod
    def worlds_students_per_country_statistics(cls):  # pylint: disable=invalid-name
        """
        Total of students amount per country to display on world map from all instances per previous calendar day.

        Returns:
            world_students_per_country (dict): Country-count accordance as pair of key-value.
        """

        start_of_day, end_of_day = get_previous_day_start_and_end_dates()

        # Get list of instances`s students per country data as unicode strings.
        students_per_country = cls.objects.filter(
            data_update__gte=start_of_day, data_update__lt=end_of_day
        ).values_list('students_per_country', flat=True)

        # Convert unicode strings into native dictionaries.
        students_per_country = [json.loads(students_per_country[instance_students]) for instance_students
                                in range(len(students_per_country))]

        world_students_per_country = defaultdict(int)

        for instance_students in students_per_country:
            for country, count in instance_students.iteritems():
                world_students_per_country[country] += count

        return dict(world_students_per_country.items())
