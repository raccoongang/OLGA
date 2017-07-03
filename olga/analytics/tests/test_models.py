"""
Tests for analytics models.
"""

from datetime import date, datetime

from mock import patch

from django.test import TestCase

from factories import InstallationStatisticsFactory
from olga.analytics.models import InstallationStatistics, get_previous_day_start_and_end_dates


class TestInstallationStatisticsMethods(TestCase):
    """
    Tests for InstallationStatistics model's core methods, that work with database.
    """

    @patch('django.utils.timezone.now')
    def setUp(self, mock_timezone_now):
        """
        Creates five unique edx installations and corresponding statistics, then create two statistics objects
        for acquainted edx installation (last two edx installation objects in unique list).

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

    def test_timeline_method_returns_unique_existing_datetime_sorted_in_descending_order(self):
        """
        Verifies that timeline method returns unique existing datetime sorted in descending order.
        """

        result = InstallationStatistics.timeline()

        self.assertEqual(
            ['2017-06-01', '2017-06-02', '2017-06-03', '2017-06-04', '2017-06-05'], result
        )

    def test_data_per_period_method_annotate_by_day_with_trunc_and_then_sums_statistics_amounts(self):
        """
        Verifies that data_per_period method annotate by day with trunc and then sums statistics amounts.
        """

        result = InstallationStatistics.data_per_period()

        self.assertEqual(
            ([10, 5, 10, 10, 10], [2, 1, 2, 2, 2], [2, 1, 2, 2, 2]), result
        )

    @patch('olga.analytics.models.get_previous_day_start_and_end_dates')
    def test_overall_counts_method_returns_overall_statistics_instance_counts_for_previous_calendar_day(
            self, mock_get_previous_day_start_and_end_dates
    ):
        """
        Verifies that test_overall_counts method returns overall statistics instance counts for previous calendar day.
        """

        mock_get_previous_day_start_and_end_dates.return_value = date(2017, 6, 1), date(2017, 6, 2)

        result = InstallationStatistics.overall_counts()

        self.assertEqual(
            (2, 2, 10), result
        )

    @patch('olga.analytics.models.get_previous_day_start_and_end_dates')
    def test_get_worlds_students_per_country_count_accordance_method_returns_correct_accordance_as_dict(
            self, mock_get_previous_day_start_and_end_dates
    ):
        """
        Verifies that test_get_worlds_students_per_country_count_accordance method returns correct accordance as dict.
        """

        mock_get_previous_day_start_and_end_dates.return_value = date(2017, 6, 1), date(2017, 6, 2)

        result = InstallationStatistics.get_worlds_students_per_country_count_accordance()

        country_count_accordance_for_previous_calendar_day = {
            'RU': 5264,
            'CA': 37086,
            'UA': 4022,
            'null': 2
        }

        self.assertDictEqual(country_count_accordance_for_previous_calendar_day, result)

    def test_create_worlds_students_per_country_data_formatted_to_render_method_returns_datamap_and_tabular_lists(self):
        """
        Verifies that test_create_worlds_students_per_country_data_formatted_to_render method
        returns datamap and tabular lists.
        """

        worlds_students_per_country = {
            'RU': 5264,
            'CA': 37086,
            'UA': 4022,
            'null': 2
        }

        datamap_format_countries_list, tabular_format_countries_list = \
            InstallationStatistics.create_worlds_students_per_country_data_formatted_to_render(
                worlds_students_per_country
            )

        self.assertEqual(
            (
                [['RUS', 5264], ['CAN', 37086], ['UKR', 4022]],
                [['CAN', 37086, '79.97'], ['RUS', 5264, '11.35'], ['UKR', 4022, '8.67'], ('Unset', 2, '~0')]
            ),
            (
                datamap_format_countries_list, tabular_format_countries_list
            )
        )

    @patch('olga.analytics.models.get_previous_day_start_and_end_dates')
    def test_get_worlds_students_per_country_data_to_render_method_returns_data_to_render_correct_values(
            self, mock_get_previous_day_start_and_end_dates
    ):
        """
        Verifies that test_get_worlds_students_per_country_data_to_render method returns data to render correct values.
        """

        mock_get_previous_day_start_and_end_dates.return_value = date(2017, 6, 1), date(2017, 6, 2)

        result = InstallationStatistics.get_worlds_students_per_country_data_to_render()

        self.assertEqual(
            (
                3,
                [['RUS', 5264], ['CAN', 37086], ['UKR', 4022]],
                [['CAN', 37086, '79.97'], ['RUS', 5264, '11.35'], ['UKR', 4022, '8.67'], ('Unset', 2, '~0')]
            ),
            result
        )


class TestInstallationStatisticsHelpMethods(TestCase):
    """
    Tests for InstallationStatistics model's help methods, that work with calculation.
    """

    def test_get_student_amount_percentage_method_returns_correct_value_if_it_is_not_too_small(self):
        """
        Verifies that test_get_student_amount_percentage method returns correct value if it is not too small.
        """
        country_count_in_statistics = 40
        all_active_students_in_statistics = 100

        result = InstallationStatistics.get_student_amount_percentage(
            country_count_in_statistics, all_active_students_in_statistics
        )

        self.assertEqual('40.00', result)

    def test_get_student_amount_percentage_method_returns_correct_value_if_it_is_too_small(self):
        """
        Verifies that test_get_student_amount_percentage method returns correct value if it is too small.
        """

        country_count_in_statistics = 3
        all_active_students_in_statistics = 348214

        result = InstallationStatistics.get_student_amount_percentage(
            country_count_in_statistics, all_active_students_in_statistics
        )

        self.assertEqual('~0', result)

    def test_is_country_exists_method_returns_true_if_country_exists(self):
        """
        Verifies that test_is_country_exists method returns true if country exists.
        """

        country = 'Canada'

        result = InstallationStatistics.is_country_exists(country)

        self.assertTrue(result)

    def test_append_country_data_to_list_method_appends_data_without_student_amount_percentage(self):
        """
        Verifies that test_append_country_data_to_list method appends data without student amount percentage.
        """

        country_list = []
        student_amount_percentage = None

        first_country, second_country = 'CA', 'UA'
        first_country_count, second_second_country = 1321, 3421

        InstallationStatistics.append_country_data_to_list(
            country_list, first_country, first_country_count, student_amount_percentage
        )

        InstallationStatistics.append_country_data_to_list(
            country_list, second_country, second_second_country, student_amount_percentage
        )

        self.assertEqual(
            [['CAN', 1321], ['UKR', 3421]], country_list
        )

    def test_append_country_data_to_list_method_appends_data_with_student_amount_percentage(self):
        """
        Verifies that test_append_country_data_to_list method appends data with student amount percentage.
        """

        country_list = []

        first_country, second_country, first_student_amount_percentage = 'CA', 'UA', 30.45
        first_country_count, second_second_country, second_student_amount_percentage = 1321, 3421, 75.01

        InstallationStatistics.append_country_data_to_list(
            country_list, first_country, first_country_count, first_student_amount_percentage
        )

        InstallationStatistics.append_country_data_to_list(
            country_list, second_country, second_second_country, second_student_amount_percentage
        )

        self.assertEqual(
            [['CAN', 1321, 30.45], ['UKR', 3421, 75.01]], country_list
        )

    def test_get_countries_amount_method_returns_countries_amount_in_tabular_format_countries_list_if_it_exists(self):
        """
        Verifies that test_get_countries_amount method returns
        countries amount in tabular format countries list if it exists.
        """

        tabular_format_countries_list = [
            ['CAN', 37086, '79.97'], ['RUS', 5264, '11.35'], ['UKR', 4022, '8.67'], ('Unset', 2, '~0')
        ]

        result = InstallationStatistics.get_countries_amount(tabular_format_countries_list)

        self.assertEqual(3, result)

    def test_get_countries_amount_method_returns_countries_amount_in_tabular_format_countries_list_if_it_is_empty(self):
        """
        Verifies that test_get_countries_amount method returns
        countries amount in tabular format countries list if it is empty.
        """

        tabular_format_countries_list = []

        result = InstallationStatistics.get_countries_amount(tabular_format_countries_list)

        self.assertEqual(0, result)


class TestAnalyticsModelsHelpFunctions(TestCase):
    """
    Tests for Analytics models help functions.
    """

    @patch('olga.analytics.models.date')
    def test_get_previous_day_start_and_end_dates(self, mock_date):
        """
        Verifies that get_previous_day_start_and_end_dates returns expected previous day start and end dates.
        """

        mock_date.today.return_value = date(2017, 6, 14)

        result = get_previous_day_start_and_end_dates()

        self.assertEqual(
            (date(2017, 6, 13), date(2017, 6, 14)), result
        )
