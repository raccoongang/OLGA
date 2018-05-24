"""
Models for analytics application. Models used to store and operate all data received from the edx platform.
"""

from __future__ import division

from datetime import date, timedelta, datetime

import operator
import pycountry
import pytz

from django.contrib.postgres.fields import JSONField
from django.db import models
from django.db.models import Sum, Count, DateField
from django.db.models.expressions import F, Func, Value
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
    uid = models.CharField(null=True, max_length=32)

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
    registered_students = models.IntegerField(default=0)
    enthusiastic_students = models.IntegerField(default=0)
    generated_certificates = models.IntegerField(default=0)
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
    unspecified_country_name = 'Country is not specified'

    @staticmethod
    def get_statistics_top_country(tabular_countries_list):
        """
        Get first country from tabular format country list.

        List is sorted, first country is a top active students rank country.
        :param tabular_countries_list: list of the two elements tuples
        :return: top country name as a string
        """
        if not tabular_countries_list:
            return ''

        return tabular_countries_list[0][0]

    @classmethod
    def get_stats_for_the_date(cls, statistics_date, edx_installation_object=None):
        """
        Provide statistic model instance for the given Edx installation.

        :param edx_installation_object: specific installation object.
        :return: statistic model instance if it is created at the specified day otherwise None
        """
        stat_item = cls.objects.filter(
            edx_installation=edx_installation_object,
            data_created_datetime__gte=statistics_date,
            data_created_datetime__lt=(statistics_date + timedelta(days=1))
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
        ).values('date_in_days').order_by('date_in_days')

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
        Total of students amount per country to display on world map from all instances per month.

        Returns:
            world_students_per_country (dict): Country-count accordance as pair of key-value.
        """
        # Get list of instances's students per country data as unicode strings.
        queryset = cls.objects.annotate(
            month_verbose=Func(
                F('data_created_datetime'), Value('TMMonth YYYY'), function='to_char'
            ),
            month_ordering=Func(
                F('data_created_datetime'), Value('YYYY-MM'), function='to_char'
            ),
        )
        result_rows = queryset.values_list(
            'month_ordering', 'month_verbose', 'students_per_country'
        )

        return cls.aggregate_countries_by_months(result_rows)

    @classmethod
    def aggregate_countries_by_months(cls, values_list):
        """
        Aggregate all the months and countries data by the month.

        :param values_list: list queryset result with three elements for every row
        :return: dictionary of months with the student countries statistics
        """
        months = {}

        for month_ordering, month_verbose, countries in values_list:
            cls.add_month_countries_data(
                month_ordering, month_verbose, countries, months
            )

        return months

    @classmethod
    def add_month_countries_data(
            cls, month_ordering, month_verbose, countries, months
    ):
        """
        Add a month data to the months dictionary.

        :param month_ordering: sortable date key represented as a string
        :param month_verbose: human friendly date represented as a string
        :param countries: dictionary of countries where the key is the country code and
            the value is the amount of the students
        :param months: dictionary that needs to be updated by the data, passed to the method
        """
        if month_ordering not in months:
            months[month_ordering] = {
                'countries': countries,
                'label': month_verbose,
            }
            return

        cls.add_up_new_month_data(months[month_ordering]['countries'], countries)

    @classmethod
    def add_up_new_month_data(cls, existing_data, new_data):
        """
        Add a new month data to the resulting data dictionary.

        Adds the counts from the new countries data dictionary to the existing ones or adds
        new countries if the don't exist in the existing_data
        """
        for existent_key in existing_data.keys():
            existing_data[existent_key] += new_data.pop(existent_key, 0)

        existing_data.update(new_data)

    @classmethod
    def create_students_per_country(cls, worlds_students_per_country):
        """
        Create convenient and necessary data formats to render it from view.

        Graphs require list-format data.
        """
        datamap_format_countries_list = []
        tabular_format_countries_map = {}

        if not worlds_students_per_country:
            tabular_format_countries_map[cls.unspecified_country_name] = [0, 0]
            return datamap_format_countries_list, tabular_format_countries_map.items()

        all_active_students = sum(worlds_students_per_country.itervalues())

        for country, count in worlds_students_per_country.iteritems():
            student_amount_percentage = cls.get_student_amount_percentage(count, all_active_students)

            try:
                country_info = pycountry.countries.get(alpha_2=country)
                country_alpha_3 = country_info.alpha_3.encode("utf8")
                datamap_format_countries_list += [[country_alpha_3, count]]

                country_name = country_info.name.encode("utf8")
            except KeyError:
                # Create students without country amount.
                country_name = cls.unspecified_country_name

            if country_name in tabular_format_countries_map:
                tabular_format_countries_map[country_name] = map(
                    operator.add,
                    tabular_format_countries_map[country_name],
                    [count, student_amount_percentage]
                )
            else:
                tabular_format_countries_map[country_name] = [count, student_amount_percentage]

        # Pop out the unspecified country
        unspecified_country_values = tabular_format_countries_map.pop(cls.unspecified_country_name, None)

        # Sort in descending order.
        tabular_format_countries_list = sorted(
            tabular_format_countries_map.items(),
            key=lambda x: x[1][0],
            reverse=True
        )

        if unspecified_country_values:
            tabular_format_countries_list.append(
                (cls.unspecified_country_name, unspecified_country_values)
            )

        return datamap_format_countries_list, tabular_format_countries_list

    @classmethod
    def get_students_per_country(cls):
        """
        Gather convenient and necessary data formats to render it from view.
        """
        months = cls.get_students_per_country_stats()

        for month in months.values():
            datamap_list, tabular_list = cls.create_students_per_country(month['countries'])
            month['datamap_countries_list'] = datamap_list
            month['tabular_countries_list'] = tabular_list
            month['top_country'] = cls.get_statistics_top_country(tabular_list)
            month['countries_amount'] = (
                len(month['countries']) - (cls.unspecified_country_name in month['countries'])
            )

        return months

    @staticmethod
    def get_student_amount_percentage(country_count_in_statistics, all_active_students):
        """
        Calculate student amount percentage based on total countries amount and particular county amount comparison.
        """
        if all_active_students == 0:
            return 0

        students_amount_percentage = int(country_count_in_statistics / all_active_students * 100)
        return students_amount_percentage

    @classmethod
    def get_students_countries_amount(cls, months):
        """
        Provide countries amount from students per country statistics as table.

        Calculate countries amount in world students per country statistics (from tabular countries list).
        Tabular format countries list can be empty - countries amount is zero.
        Tabular format countries list can be not empty - it contains particular country-count accordance
        and `Country is not specified` field, that has students without country amount.

        Actually `Country is not specified` field is not a country, so it does not fill up in countries amount.
        """
        countries_amount = 0

        for month in months.values():
            countries = dict(month['tabular_countries_list'])
            countries.pop(cls.unspecified_country_name, None)
            countries_amount += len(countries)

        return countries_amount

    def update(self, stats):
        """
        Update model from given dictionary and save it.

        :param stats: dictionary with new data.
        """
        for (key, value) in stats.items():
            setattr(self, key, value)
        self.save()
