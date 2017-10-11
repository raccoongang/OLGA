"""
Models for analytics application. Models used to store and operate all data received from the edx platform.
"""

from __future__ import division

from collections import defaultdict
from datetime import date, timedelta, datetime

import pycountry

from django.contrib.postgres.fields import JSONField
from django.db import models
from django.db.models import Sum, Count, DateField
from django.db.models.functions import Trunc


def get_last_calendar_day():
    """
    Get accurate start and end dates, that create segment between them equal to a full last calendar day.

    Returns:
        start_of_day (date): Previous day's start. Example for 2017-05-15 is 2017-05-15.
        end_of_day (date): Previous day's end, it's a next day (tomorrow) toward day's start,
                           that doesn't count in segment. Example for 2017-05-15 is 2017-05-16.
    """
    end_of_day = date.today()
    start_of_day = end_of_day - timedelta(days=1)

    return start_of_day, end_of_day


class EdxInstallation(models.Model):
    """
    Model that stores overall data received from the edx-platform.
    """

    access_token = models.UUIDField(null=True)
    platform_name = models.CharField(max_length=255, null=True, blank=True)
    platform_url = models.URLField(null=True, blank=True)

    latitude = models.FloatField(
        null=True, blank=True, help_text='Latitude coordinate of edX platform follows `float` type. Example: 50.10'
    )

    longitude = models.FloatField(
        null=True, blank=True, help_text='Longitude coordinate of edX platform follows `float` type. Example: 40.05'
    )


class InstallationStatistics(models.Model):
    """
    Model that stores statistics data received from the edx-platform.
    """

    active_students_amount_day = models.IntegerField(default=0)
    active_students_amount_week = models.IntegerField(default=0)
    active_students_amount_month = models.IntegerField(default=0)
    courses_amount = models.IntegerField(default=0)
    data_created_datetime = models.DateTimeField(auto_now_add=True)
    edx_installation = models.ForeignKey(EdxInstallation)
    statistics_level = models.CharField(
        choices=(
            ('enthusiast', 'enthusiast'),
            ('paranoid', 'paranoid'),
        ),
        max_length=255,
        default='paranoid'
    )
    students_per_country = JSONField(
        default={},
        blank=True,
        null=True,
        help_text='This field has students country-count accordance. It follows `json` type. '
                  'Example: {"RU": 2632, "CA": 18543, "UA": 2011, "null": 1}'
    )

    @classmethod
    def get_stats_for_this_day(cls, edx_installation_object=None):
        """
        Provide model, for given installation object, that was created today, or None if it not exist.

        :param edx_installation_object: specific installation object.
        """
        today_midnight = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        stat_item = cls.objects.filter(
            edx_installation=edx_installation_object,
            data_created_datetime__gte=today_midnight
        ).last()
        return stat_item

    @classmethod
    def timeline(cls):
        """
        Provide timeline in days for plotting on x axis.
        """
        timeline_datetimes = cls.objects.order_by(
            'data_created_datetime'
        ).values_list('data_created_datetime', flat=True).distinct()

        timeline_dates = [x.date().strftime('%Y-%m-%d') for x in timeline_datetimes]

        # Support case, when data are sent more often, for example when testing every 15 seconds.
        # Then filter unique and sort back, because timeline should be ordered.
        timeline_dates = sorted(set(timeline_dates))

        return timeline_dates

    @classmethod
    def data_per_period(cls):
        """
        Provide total students, courses and instances, from all services per period, day by default.

        We summarize values per day, because in same day we can receive data from multiple different instances.
        We suppose, that every instance send data only once per day.
        """
        subquery = cls.objects.annotate(
            date_in_days=Trunc('data_created_datetime', 'day', output_field=DateField())
        ).values('date_in_days').order_by()

        # last order_by() is needed:
        # http://chase-seibert.github.io/blog/2012/02/24/django-aggregation-group-by-day.html
        # https://docs.djangoproject.com/en/dev/topics/db/aggregation/#interaction-with-default-ordering-or-order-by

        students_per_day = subquery.annotate(
            students=Sum('active_students_amount_day')
        ).values_list('students', flat=True)

        courses_per_day = subquery.annotate(courses=Sum('courses_amount')).values_list('courses', flat=True)

        instances_per_day = subquery.annotate(
            instances=Count('edx_installation__access_token')
        ).values_list('instances', flat=True)

        return list(students_per_day), list(courses_per_day), list(instances_per_day)

    @classmethod
    def overall_counts(cls):
        """
        Provide total count of all instances, courses and students from all instances per previous calendar day.

        Returns overall counts as int-value.
        """
        start_of_day, end_of_day = get_last_calendar_day()

        all_unique_instances = cls.objects.filter(
            data_created_datetime__gte=start_of_day, data_created_datetime__lt=end_of_day
        )

        instances_count = all_unique_instances.count()

        courses_count = all_unique_instances.aggregate(
            Sum('courses_amount')
        )['courses_amount__sum']

        students_count = all_unique_instances.aggregate(
            Sum('active_students_amount_day')
        )['active_students_amount_day__sum']

        return instances_count, courses_count, students_count

    @classmethod
    def get_students_per_country_stats(cls):
        """
        Total of students amount per country to display on world map from all instances per previous calendar day.

        Returns:
            world_students_per_country (dict): Country-count accordance as pair of key-value.
        """
        start_of_day, end_of_day = get_last_calendar_day()

        # Get list of instances's students per country data as unicode strings.
        students_per_country = cls.objects.filter(
            data_created_datetime__gte=start_of_day, data_created_datetime__lt=end_of_day
        ).values_list('students_per_country', flat=True)

        world_students_per_country = defaultdict(int)

        for instance_students in students_per_country:
            for country, count in instance_students.iteritems():
                world_students_per_country[country] += count

        return world_students_per_country

    @classmethod
    def create_students_per_country(cls, worlds_students_per_country):
        """
        Create convenient and necessary data formats to render it from view.

        Graphs require list-format data.
        """
        datamap_format_countries_list = []
        tabular_format_countries_list = []

        if not worlds_students_per_country:
            tabular_format_countries_list.append(['Unset', 0, 0])
            return datamap_format_countries_list, tabular_format_countries_list

        all_active_students = sum(worlds_students_per_country.itervalues())

        for country, count in worlds_students_per_country.iteritems():
            student_amount_percentage = cls.get_student_amount_percentage(count, all_active_students)

            if country != 'null':
                country_alpha_3 = str(pycountry.countries.get(alpha_2=country).alpha_3)
                datamap_format_countries_list += [[country_alpha_3, count]]

                country_name = str(pycountry.countries.get(alpha_2=country).name)
                tabular_format_countries_list += [[country_name, count, student_amount_percentage]]

            else:
                # Create students without country amount.
                tabular_format_countries_list += [['Unset', count, student_amount_percentage]]

        # Sort in descending order.
        tabular_format_countries_list.sort(key=lambda row: row[1], reverse=True)

        return datamap_format_countries_list, tabular_format_countries_list

    @classmethod
    def get_students_per_country(cls):
        """
        Gather convenient and necessary data formats to render it from view.
        """
        students_per_country = cls.get_students_per_country_stats()

        datamap_format_countries_list, tabular_format_countries_list = \
            cls.create_students_per_country(students_per_country)

        return datamap_format_countries_list, tabular_format_countries_list

    @staticmethod
    def get_student_amount_percentage(country_count_in_statistics, all_active_students):
        """
        Calculate student amount percentage based on total countries amount and particular county amount comparison.
        """
        students_amount_percentage = int(country_count_in_statistics / all_active_students * 100)
        return students_amount_percentage

    @classmethod
    def get_students_countries_amount(cls):
        """
        Provide countries amount from students per country statistics as table.

        Calculate countries amount in world students per country statistics (from tabular countries list).
        Tabular format countries list can be empty - countries amount is zero.
        Tabular format countries list can be not empty - it contains particular country-count accordance
        and `Unset` field, that has students without country amount.

        Actually `Unset` field is not a country, so it does not fill up in countries amount.
        """
        _, tabular_format_countries_list = cls.get_students_per_country()
        countries_amount = len(tabular_format_countries_list) - 1

        return countries_amount

    def update(self, stats):
        """
        Update model from given dictionary and save it.

        :param stats: dictionary with new data.
        """
        for (key, value) in stats.items():
            setattr(self, key, value)
        self.save()
