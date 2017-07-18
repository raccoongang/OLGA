"""
Models for analytics application. Models used to store and operate all data received from the edx platform.
"""

from __future__ import division

from datetime import date, timedelta
import json
from collections import defaultdict

import pycountry

from django.db import models
from django.db.models import Sum, Count, DateField
from django.db.models.functions import Trunc


def get_previous_day_start_and_end_dates():  # pylint: disable=invalid-name
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
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    def does_edx_installation_extend_level_first_time(self):  # pylint: disable=invalid-name
        """
        Check if edx installation extends statistics level first time.
        If platform url exists It means edx installation already has overall information about itself.
        Returns False and do nothing.
        If platform url does not exist It means edx installation extended statistics level first time.
        Returns True and go to update edx installation's overall information.
        """
        return not self.platform_url

    def update_edx_instance_info(self, enthusiast_edx_installation):
        """
        Besides existing edx installation access token - extended statistics level requires a bit more information.
        Update blank object fields: latitude, longitude, platform_name and platform_url content.
        """
        self.latitude = enthusiast_edx_installation['latitude']
        self.longitude = enthusiast_edx_installation['longitude']
        self.platform_name = enthusiast_edx_installation['platform_name']
        self.platform_url = enthusiast_edx_installation['platform_url']
        self.save()


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
    students_per_country = models.TextField()

    @classmethod
    def timeline(cls):
        """
        Provide timeline in days for plotting on x axis.
        """
        timeline_datetimes = cls.objects.order_by(
            'data_created_datetime'
        ).values_list('data_created_datetime', flat=True).distinct()

        timeline_dates = [x.date().strftime('%Y-%m-%d') for x in timeline_datetimes]

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
        start_of_day, end_of_day = get_previous_day_start_and_end_dates()

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
        start_of_day, end_of_day = get_previous_day_start_and_end_dates()

        # Get list of instances's students per country data as unicode strings.
        students_per_country = cls.objects.filter(
            data_created_datetime__gte=start_of_day, data_created_datetime__lt=end_of_day
        ).values_list('students_per_country', flat=True)

        students_per_country = [json.loads(instance_students) for instance_students in students_per_country]

        world_students_per_country = defaultdict(int)

        for instance_students in students_per_country:
            for country, count in instance_students.iteritems():
                world_students_per_country[country] += count

        return dict(world_students_per_country.items())

    @staticmethod
    def get_student_amount_percentage(country_count_in_statistics, all_active_students):
        """
        Calculate student amount percentage based on total countries amount and particular county amount comparison.
        If percentage is too small and doesn't show real numbers
        it will be changed to '~0' (around zero value, but not totally).
        """
        students_amount_percentage = format(
            country_count_in_statistics / all_active_students * 100, '.2f'
        )

        if students_amount_percentage == '0.00':
            students_amount_percentage = '~0'

        return students_amount_percentage

    @staticmethod
    def does_country_exists(country):
        """
        Check if value is not a null.
        """
        return country != 'null'

    @classmethod
    def create_students_per_country_to_render(cls, worlds_students_per_country):
        # pylint: disable=invalid-name
        """
        Create convenient and necessary data formats to render it from view.
        Graphs require list-format data.
        """
        datamap_format_countries_list = []
        tabular_format_countries_list = []

        if not worlds_students_per_country:
            tabular_format_countries_list.append(('Unset', 0, 0))
            return datamap_format_countries_list, tabular_format_countries_list

        all_active_students = sum(worlds_students_per_country.itervalues())

        for country, count in worlds_students_per_country.iteritems():
            student_amount_percentage = cls.get_student_amount_percentage(count, all_active_students)

            if cls.does_country_exists(country):
                country = str(pycountry.countries.get(alpha_2=country).alpha_3)

                datamap_format_countries_list += [[country, count]]
                tabular_format_countries_list += [[country, count, student_amount_percentage]]

            else:
                # Create students without country amount.
                tabular_format_countries_list += [['Unset', count, student_amount_percentage]]

        # Sort in descending order.
        tabular_format_countries_list.sort(key=lambda row: row[1], reverse=True)

        return datamap_format_countries_list, tabular_format_countries_list

    @classmethod
    def get_students_per_country_to_render(cls):
        # pylint: disable=invalid-name
        """
        Gather convenient and necessary data formats to render it from view.
        """
        students_per_country = cls.get_students_per_country_stats()

        datamap_format_countries_list, tabular_format_countries_list = \
            cls.create_students_per_country_to_render(students_per_country)

        return datamap_format_countries_list, tabular_format_countries_list

    @staticmethod
    def calculate_countries_amount(tabular_format_countries_list):
        """
        Calculate countries amount in worlds students per country statistics as table.

        Tabular format countries list can be empty - countries amount is zero.
        Tabular format countries list can be not empty - it contains particular country-count accordance
        and `Unset` field, that has students without country amount.

        Actually `Unset` field is not a country, so it does not fill up in countries amount.
        """
        if not tabular_format_countries_list:
            return 0

        # Exclude `Unset` country from countries amount.
        return len(tabular_format_countries_list) - 1

    @classmethod
    def get_students_countries_amount(cls):
        """
        Provide countries amount from students per country statistics as table.
        """
        _, tabular_format_countries_list = cls.get_students_per_country_to_render()
        countries_amount = cls.calculate_countries_amount(tabular_format_countries_list)

        return countries_amount
