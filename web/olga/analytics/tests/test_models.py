# coding=utf-8
"""
Tests for analytics models.
"""
from collections import OrderedDict
from copy import deepcopy
from datetime import date, datetime

from ddt import ddt, data, unpack
from mock import patch

from django.test import TestCase

from olga.analytics.tests.factories import InstallationStatisticsFactory
from olga.analytics.models import InstallationStatistics, get_last_calendar_day

# pylint: disable=invalid-name, attribute-defined-outside-init

EXPECTED_CLEAN_DATAMAP_FORMAT_COUNTRIES_LIST = [
    ['ALA', 2922],
    ['RUS', 5264],
    ['CAN', 37086],
    ['UKR', 4022],
]

# "<number> / 2 * 9" - is the operation from the TestInstallationStatisticsMethods.setUp
EXPECTED_DATAMAP_FORMAT_COUNTRIES_LIST = [[a, b / 2 * 9] for a, b in EXPECTED_CLEAN_DATAMAP_FORMAT_COUNTRIES_LIST]

EXPECTED_CLEAN_TABULAR_FORMAT_COUNTRIES_LIST = [
    ('Canada', [37086, 75]),
    ('Russian Federation', [5264, 10]),
    ('Ukraine', [4022, 8]),
    ('Åland Islands', [2922, 5]),
    (InstallationStatistics.unspecified_country_name, [6, 0]),
]

# "<number> / 2 * 9" - is the operation from the TestInstallationStatisticsMethods.setUp
EXPECTED_TABULAR_FORMAT_COUNTRIES_LIST = [
    (a, [b[0] / 2 * 9, b[1]]) for a, b in EXPECTED_CLEAN_TABULAR_FORMAT_COUNTRIES_LIST
]

WORLDS_STUDENTS_PER_COUNTRY = {
    '2017-06': {
        'label': 'June 2017',
        'countries': {
            'AX': 2922,
            'RU': 5264,
            'CA': 37086,
            'UA': 4022,
            'null': 2,
            '': 2,
            'missing country': 2,
        },
        'datamap_countries_list': EXPECTED_DATAMAP_FORMAT_COUNTRIES_LIST,
        'tabular_countries_list': EXPECTED_TABULAR_FORMAT_COUNTRIES_LIST,
    }
}


class TestInstallationStatisticsMethods(TestCase):
    """
    Tests for InstallationStatistics model's core methods, that work with database.
    """

    @patch('django.utils.timezone.now')
    def setUp(self, mock_timezone_now):  # pylint: disable=arguments-differ
        """
        Create five unique edx installations and corresponding statistics.
        Create two statistics objects for acquainted edx installation (last two edx installation objects in unique list)

        So we get 5 unique objects, 3 from them has only one record in installation statistics,
        2 of them has 2 records by one for last two unique objects.

        Let me show full description for clearer understanding:
            - first edx installation object with 2017-06-01 15:30:30 statistics object by time.
            - second object with 2017-06-01 15:30:30
            - third object with 2017-06-01 15:30:30
            - fourth object with 2017-06-01 15:30:30, 2017-06-04 15:30:30, 2017-06-05 15:30:30
            - fifth object with 2017-06-01 15:30:30, 2017-06-04 15:30:30, 2017-06-05 15:30:30
        """
        students_division_by_2_part = OrderedDict([
            (k, v / 2) for k, v in WORLDS_STUDENTS_PER_COUNTRY['2017-06']['countries'].iteritems()
        ])

        data_created_datetimes = [
            datetime(2017, 6, 1, 15, 30, 30),
            datetime(2017, 6, 1, 15, 30, 30),
            datetime(2017, 6, 2, 15, 30, 30),
            datetime(2017, 6, 3, 15, 30, 30),
            datetime(2017, 6, 3, 15, 30, 30),
        ]

        for data_created_datetime in data_created_datetimes:
            mock_timezone_now.return_value = data_created_datetime
            InstallationStatisticsFactory(
                data_created_datetime=data_created_datetime,
                students_per_country=students_division_by_2_part
            )

        data_created_datetimes_for_acquainted_edx_installation = [
            datetime(2017, 6, 4, 15, 30, 30),
            datetime(2017, 6, 5, 15, 30, 30),
        ]

        for data_created_datetime in data_created_datetimes_for_acquainted_edx_installation:
            mock_timezone_now.return_value = data_created_datetime

            InstallationStatisticsFactory(
                data_created_datetime=data_created_datetime,
                edx_installation=InstallationStatistics.objects.all()[4].edx_installation,
                students_per_country=students_division_by_2_part
            )

            InstallationStatisticsFactory(
                data_created_datetime=data_created_datetime,
                edx_installation=InstallationStatistics.objects.all()[5].edx_installation,
                students_per_country=students_division_by_2_part
            )

    def test_timeline(self):
        """
        Verify that timeline method returns unique existing datetime sorted in descending order.
        """
        result = InstallationStatistics.timeline()

        self.assertEqual(
            ['2017-06-01', '2017-06-02', '2017-06-03', '2017-06-04', '2017-06-05'], result
        )

    def test_data_per_period(self):
        """
        Verify that data_per_period method annotates by day with trunc and then sums statistics amounts.
        """
        result = InstallationStatistics.data_per_period()

        self.assertEqual(
            ([10, 5, 10, 10, 10], [2, 1, 2, 2, 2], [2, 1, 2, 2, 2]), result
        )

    @patch('olga.analytics.models.get_last_calendar_day')
    def test_overall_counts(self, mock_get_last_calendar_day):
        """
        Verify that overall_counts method returns overall statistics instance counts for previous calendar day.
        """
        mock_get_last_calendar_day.return_value = date(2017, 6, 1), date(2017, 6, 2)

        result = InstallationStatistics.overall_counts()

        self.assertEqual(
            (2, 2, 10), result
        )

    def test_students_per_country_as_dict(self):
        """
        Verify that get_students_per_country_stats method returns correct accordance as dict.
        """
        result = InstallationStatistics.get_students_per_country_stats()
        wanted_result = {}

        for key, value in WORLDS_STUDENTS_PER_COUNTRY['2017-06']['countries'].iteritems():
            wanted_result[key] = value * 9 / 2

        self.assertDictEqual(wanted_result, result['2017-06']['countries'])

    def test_datamap_and_tabular_lists(self):
        """
        Verify that view gets datamap and tabular lists with corresponding model method.
        Model method is create_students_per_country.

        """
        result_datamap, result_tabular = InstallationStatistics.create_students_per_country(
            WORLDS_STUDENTS_PER_COUNTRY['2017-06']['countries']
        )
        result_datamap = self.sort_datamap_list(result_datamap)
        wanted_datamap = self.sort_datamap_list(EXPECTED_CLEAN_DATAMAP_FORMAT_COUNTRIES_LIST)

        self.assertEqual(wanted_datamap, result_datamap)
        self.assertEqual(EXPECTED_CLEAN_TABULAR_FORMAT_COUNTRIES_LIST, result_tabular)

    @staticmethod
    def sort_datamap_list(datamap_list):
        """
        Sort datamap list to cast it into the sorted form that will be tested later in comparison.
        """
        return sorted(
            datamap_list,
            key=lambda x: x[1],
            reverse=True
        )

    def test_students_per_country_render(self):
        """
        Verify that get_students_per_country method returns data to render correct values.
        """
        months = InstallationStatistics.get_students_per_country()
        datamap_list = self.sort_datamap_list(months['2017-06']['datamap_countries_list'])
        tabular_list = months['2017-06']['tabular_countries_list']
        self.assertEqual(EXPECTED_TABULAR_FORMAT_COUNTRIES_LIST, tabular_list)

        for i in datamap_list:
            self.assertIn(i, EXPECTED_DATAMAP_FORMAT_COUNTRIES_LIST)

    def test_get_students_countries_amount(self):
        """
        Test get_students_countries_amount method of the Installation statistics.
        """
        countries_amount = InstallationStatistics.get_students_countries_amount(
            deepcopy(WORLDS_STUDENTS_PER_COUNTRY)
        )

        self.assertEqual(countries_amount, 4)

    def test_get_statistics_top_country_empty(self):
        """
        Test get_statistics_top_country method of the Installation statistics with an empty parameter.
        """
        top_country_name_empty = InstallationStatistics.get_statistics_top_country([])

        self.assertEqual(top_country_name_empty, '')


@ddt
class TestInstallationStatisticsHelpMethods(TestCase):
    """
    Tests for InstallationStatistics model's help methods, that work with calculation.
    """

    @data([40, 100, 40], [3, 348214, 0])
    @unpack
    def test_student_percentage(self, country_count_in_statistics, all_active_students_in_statistics, expected_result):
        """
        Verify that get_student_amount_percentage method returns correct value.
        """
        result = InstallationStatistics.get_student_amount_percentage(
            country_count_in_statistics, all_active_students_in_statistics
        )

        self.assertEqual(expected_result, result)


class TestAnalyticsModelsHelpFunctions(TestCase):
    """
    Tests for Analytics models help functions.
    """

    @patch('olga.analytics.models.date')
    def test_calendar_day(self, mock_date):
        """
        Verify that get_last_calendar_day returns expected previous day start and end dates.
        """
        mock_date.today.return_value = date(2017, 6, 14)

        result = get_last_calendar_day()

        self.assertEqual(
            (date(2017, 6, 13), date(2017, 6, 14)), result
        )
