"""
Test for map metrics.
"""

import json

import pycountry

from django.test import TestCase

from olga.functional_tests.utils import SetUp, html_target

from olga.analytics.tests.factories import InstallationStatisticsFactory
from olga.analytics.models import InstallationStatistics

# pylint: disable=invalid-name


class TestMapMetricsWithoutStatistics(TestCase):
    """
    Test html render map metrics if statistics does not exist.
    """

    def test_html_renders_unset_to_top_country_activity_metrics_if_no_students_country(self):
        """
        Verify that html renders unset to country activity metric if no students country.
        """
        response = self.client.get('/map/')

        top_country = 'Unset'
        top_country_label = 'Top Country by Enrollment'

        target_html_object = html_target.activity_metric.format(top_country, top_country_label)

        self.assertContains(response, target_html_object, 1)

    def test_html_renders_zero_to_countries_in_statistics_activity_metrics_if_no_students_country(self):
        """
        Verify that html renders zero (0) to countries in statistics activity metric if no students country.
        """
        response = self.client.get('/map/')

        countries_in_statistics = 0
        countries_in_statistics_label = 'Countries in Statistics'

        target_html_object = html_target.activity_metric.format(countries_in_statistics, countries_in_statistics_label)

        self.assertContains(response, target_html_object, 1)

    def test_html_renders_table_with_only_unset_values_to_geographic_breakdown_if_no_students_country(self):
        """
        Verify that html renders table only with unset values to geographic breakdown if no students country.
        """
        response = self.client.get('/map/')

        unset_country = 'Unset'
        unset_count, unset_percentage = 0, 0

        target_html_object_country = html_target.country_grid_cell.format(unset_country)
        target_html_object_count = html_target.country_count_grid_cell.format(unset_count)
        target_html_object_percentage = html_target.percentage_grid_cell.format(unset_percentage)

        self.assertContains(response, target_html_object_country, 1)
        self.assertContains(response, target_html_object_count, 1)
        self.assertContains(response, target_html_object_percentage, 1)


class TestMapMetricsWithStatistics(TestCase):
    """
    Test html render map metrics if statistics exists.
    """

    @staticmethod
    def setUp():
        """
        Run setup.
        """
        SetUp.setUp()

    def test_html_renders_top_country_to_activity_metrics_if_statistics_exists(self):
        """
        Verify that html renders country alpha 3 name to country activity metric if students country statistics exists.
        """
        factory_students_per_country_accordance = json.loads(InstallationStatisticsFactory.students_per_country)

        max_students_country_alpha_2 = max(
            factory_students_per_country_accordance, key=factory_students_per_country_accordance.get
        )

        max_students_country_alpha_3 = str(
            pycountry.countries.get(alpha_2=max_students_country_alpha_2).alpha_3
        )

        max_students_country_alpha_3_label = 'Top Country by Enrollment'

        target_html_object = html_target.activity_metric.format(
            max_students_country_alpha_3, max_students_country_alpha_3_label
        )

        response = self.client.get('/map/')

        self.assertContains(response, target_html_object, 1)

    def test_html_renders_countries_amount_to_countries_in_statistics_activity_metrics_if_statistics_exists(self):
        """
        Verify that html renders countries amount to activity metric if students country statistics exists.
        """
        factory_students_per_country_accordance = json.loads(InstallationStatisticsFactory.students_per_country)

        unset_also_country = 1
        countries_in_statistics = len(factory_students_per_country_accordance) - unset_also_country
        countries_in_statistics_label = 'Countries in Statistics'

        target_html_object = html_target.activity_metric.format(
            countries_in_statistics, countries_in_statistics_label
        )

        response = self.client.get('/map/')

        self.assertContains(response, target_html_object, 1)

    def test_html_renders_table_with_all_country_count_percentage_accordance_to_geographic_breakdown(self):
        """
        Verify that html renders table with all accordance to geographic table if students country statistics exists.
        """
        installation_statistics = InstallationStatistics()

        factory_students_per_country_accordance = json.loads(InstallationStatisticsFactory.students_per_country)

        all_active_students = sum(factory_students_per_country_accordance.values())

        response = self.client.get('/map/')

        for country, count in factory_students_per_country_accordance.items():
            if installation_statistics.is_country_exists(country):

                student_amount_percentage = installation_statistics.get_student_amount_percentage(
                    count, all_active_students
                )

                country_alpha_3 = str(
                    pycountry.countries.get(alpha_2=country).alpha_3
                )

                target_html_object_country = html_target.country_grid_cell.format(country_alpha_3)
                target_html_object_count = html_target.country_count_grid_cell.format(count)
                target_html_object_percentage = html_target.percentage_grid_cell.format(student_amount_percentage)

                self.assertContains(response, target_html_object_country, 1)
                self.assertContains(response, target_html_object_count, 1)
                self.assertContains(response, target_html_object_percentage, 1)
