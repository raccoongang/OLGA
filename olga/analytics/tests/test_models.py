"""
Tests for analytics models.
"""

from datetime import date, datetime

from ddt import ddt, data, unpack
from mock import patch

from django.test import TestCase

from olga.analytics.tests.factories import EdxInstallationFactory, InstallationStatisticsFactory
from olga.analytics.models import (
    EdxInstallation, InstallationStatistics, get_previous_day_start_and_end_dates
)

# pylint: disable=invalid-name, attribute-defined-outside-init


class TestEdxInstallationMethods(TestCase):
    """
    Tests for EdxInstallation model's core methods, that work with database.
    """

    @staticmethod
    def setUp():
        """
        Create one EdxInstallation object.
        """
        EdxInstallationFactory(platform_url=None)

    @staticmethod
    def fake_installation_enthusiast_level():
        """
        Create fake edx installation sends statistics with enthusiast level.

        Actually it sends a lot of data, but we need to mock only `platform_url`.
        """
        edx_installation_object = EdxInstallation.objects.first()
        edx_installation_object.platform_url = 'https://url.exists'
        edx_installation_object.save()

    def test_extending_level_first_time(self):
        """
        Verify that does_edx_installation_extend_level_first_time method return True, if not platform name.

        If edx installation has not platform name It means installation sends statistics with `paranoid` level.
        """
        edx_installation_object = EdxInstallation.objects.first()
        result = edx_installation_object.does_edx_installation_extend_level_first_time()
        self.assertEqual(True, result)

    def test_extending_level_not_first_time(self):
        """
        Verify that does_edx_installation_extend_level_first_time method return False, if platform url exists.

        If edx installation has platform name It means installation sends statistics with `enthusiast` level.
        """
        self.fake_installation_enthusiast_level()

        edx_installation_object = EdxInstallation.objects.first()
        result = edx_installation_object.does_edx_installation_extend_level_first_time()
        self.assertEqual(False, result)

    def test_update_edx_instance_info(self):
        """
        Verify that update_edx_instance_info method save edx installation enthusiast data.
        """
        enthusiast_edx_installation = {
            'latitude': 50.32,
            'longitude': 45.11,
            'platform_name': 'platform_name',
            'platform_url': 'https://platform.url'
        }

        edx_installation_object = EdxInstallation.objects.first()
        edx_installation_object.update_edx_instance_info(enthusiast_edx_installation)

        extended_edx_installation_object_attributes = edx_installation_object.__dict__

        self.assertDictContainsSubset(enthusiast_edx_installation, extended_edx_installation_object_attributes)


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
        data_created_datetimes = [
            datetime(2017, 6, 1, 15, 30, 30),
            datetime(2017, 6, 1, 15, 30, 30),
            datetime(2017, 6, 2, 15, 30, 30),
            datetime(2017, 6, 3, 15, 30, 30),
            datetime(2017, 6, 3, 15, 30, 30),
        ]

        for data_created_datetime in data_created_datetimes:
            mock_timezone_now.return_value = data_created_datetime
            InstallationStatisticsFactory(data_created_datetime=data_created_datetime)

        data_created_datetimes_for_acquainted_edx_installation = [
            datetime(2017, 6, 4, 15, 30, 30),
            datetime(2017, 6, 5, 15, 30, 30),
        ]

        for data_created_datetime in data_created_datetimes_for_acquainted_edx_installation:
            mock_timezone_now.return_value = data_created_datetime

            InstallationStatisticsFactory(
                data_created_datetime=data_created_datetime,
                edx_installation=InstallationStatistics.objects.all()[4].edx_installation
            )

            InstallationStatisticsFactory(
                data_created_datetime=data_created_datetime,
                edx_installation=InstallationStatistics.objects.all()[5].edx_installation
            )

    @staticmethod
    def create_expected_default_data():
        """
        Create datamap and tabular format lists for testing.
        """
        datamap_format_countries_list = [
            ['RUS', 5264], ['CAN', 37086], ['UKR', 4022]
        ]

        tabular_format_countries_list = [
            ['CAN', 37086, '79.97'], ['RUS', 5264, '11.35'], ['UKR', 4022, '8.67'], ['Unset', 2, '~0']
        ]

        return datamap_format_countries_list, tabular_format_countries_list

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

    @patch('olga.analytics.models.get_previous_day_start_and_end_dates')
    def test_overall_counts(self, mock_get_previous_day_start_and_end_dates):
        """
        Verify that overall_counts method returns overall statistics instance counts for previous calendar day.
        """
        mock_get_previous_day_start_and_end_dates.return_value = date(2017, 6, 1), date(2017, 6, 2)

        result = InstallationStatistics.overall_counts()

        self.assertEqual(
            (2, 2, 10), result
        )

    @patch('olga.analytics.models.get_previous_day_start_and_end_dates')
    def test_students_per_country_as_dict(
            self, mock_get_previous_day_start_and_end_dates
    ):
        """
        Verify that get_students_per_country_stats method returns correct accordance as dict.
        """
        mock_get_previous_day_start_and_end_dates.return_value = date(2017, 6, 1), date(2017, 6, 2)

        result = InstallationStatistics.get_students_per_country_stats()

        country_count_accordance_for_previous_calendar_day = {
            'RU': 5264,
            'CA': 37086,
            'UA': 4022,
            'null': 2
        }

        self.assertDictEqual(country_count_accordance_for_previous_calendar_day, result)

    def test_datamap_and_tabular_lists(self):
        """
        Verify that view gets datamap and tabular lists with corresponding model method.

        Model method is create_students_per_country_to_render.
        """
        worlds_students_per_country = {
            'RU': 5264,
            'CA': 37086,
            'UA': 4022,
            'null': 2
        }

        datamap_format_countries_list, tabular_format_countries_list = self.create_expected_default_data()

        result = InstallationStatistics.create_students_per_country_to_render(worlds_students_per_country)

        self.assertEqual(
            (datamap_format_countries_list, tabular_format_countries_list), result
        )

    @patch('olga.analytics.models.get_previous_day_start_and_end_dates')
    def test_students_per_country_render(
            self, mock_get_previous_day_start_and_end_dates
    ):
        """
        Verify that get_students_per_country_to_render method returns data to render correct values.
        """
        mock_get_previous_day_start_and_end_dates.return_value = date(2017, 6, 1), date(2017, 6, 2)

        datamap_format_countries_list, tabular_format_countries_list = self.create_expected_default_data()

        result = InstallationStatistics.get_students_per_country_to_render()

        self.assertEqual(
            (datamap_format_countries_list, tabular_format_countries_list), result
        )


@ddt
class TestInstallationStatisticsHelpMethods(TestCase):
    """
    Tests for InstallationStatistics model's help methods, that work with calculation.
    """

    @data([40, 100, '40.00'], [3, 348214, '~0'])
    @unpack
    def test_student_percentage(self, country_count_in_statistics, all_active_students_in_statistics, expected_result):
        """
        Verify that get_student_amount_percentage method returns correct value.
        """
        result = InstallationStatistics.get_student_amount_percentage(
            country_count_in_statistics, all_active_students_in_statistics
        )

        self.assertEqual(expected_result, result)

    def test_does_country_exists_if_country_exists(self):
        """
        Verify that test does_country_exists method returns true if country exists.
        """
        country = 'Canada'

        result = InstallationStatistics.does_country_exists(country)

        self.assertTrue(result)

    def test_calculate_countries_amount_if_tabular_list_exists(self):
        """
        Verify that calculate_countries_amount method returns countries amount in tabular format list if it exists.
        """
        tabular_format_countries_list = [
            ['CAN', 37086, '79.97'], ['RUS', 5264, '11.35'], ['UKR', 4022, '8.67'], ['Unset', 2, '~0']
        ]

        result = InstallationStatistics.calculate_countries_amount(tabular_format_countries_list)

        self.assertEqual(3, result)

    def test_calculate_countries_amount_if_no_tabular_list(self):
        """
        Verify that calculate_countries_amount method returns countries amount in tabular format list if it is empty.
        """
        tabular_format_countries_list = []

        result = InstallationStatistics.calculate_countries_amount(tabular_format_countries_list)

        self.assertEqual(0, result)


class TestAnalyticsModelsHelpFunctions(TestCase):
    """
    Tests for Analytics models help functions.
    """

    @patch('olga.analytics.models.date')
    def test_calendar_day(self, mock_date):
        """
        Verify that get_previous_day_start_and_end_dates returns expected previous day start and end dates.
        """
        mock_date.today.return_value = date(2017, 6, 14)

        result = get_previous_day_start_and_end_dates()

        self.assertEqual(
            (date(2017, 6, 13), date(2017, 6, 14)), result
        )
