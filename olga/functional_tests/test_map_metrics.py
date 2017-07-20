"""
Test for map metrics.
"""

import json

import pycountry
from ddt import ddt, data, unpack

from django.test import TestCase

from olga.functional_tests.utils import SetUp, html_target

from olga.analytics.tests.factories import InstallationStatisticsFactory
from olga.analytics.models import InstallationStatistics

# pylint: disable=invalid-name, attribute-defined-outside-init


@ddt
class TestMapMetricsWithoutStatistics(TestCase):
    """
    Test html render map metrics if statistics does not exist.
    """

    def setUp(self):
        """
        Provide common response.
        """
        self.response = self.client.get('/map/')

    @data([None, 'Top Country by Enrollment'], [0, 'Countries in Statistics'])
    @unpack
    def test_unset_country(self, value, label):
        """
        Verify that html renders unset to country activity metric if no students country.
        """
        target_html_object = html_target.activity_metric.format(value, label)

        self.assertContains(self.response, target_html_object, 1)

    def test_unset_value(self):
        """
        Verify that html renders table only with unset values to geographic breakdown if no students country.
        """
        unset_country = 'Unset'
        unset_count, unset_percentage = 0, 0

        target_html_object_country = html_target.country_grid_cell.format(unset_country)
        target_html_object_count = html_target.country_count_grid_cell.format(unset_count)
        target_html_object_percentage = html_target.percentage_grid_cell.format(unset_percentage)

        self.assertContains(self.response, target_html_object_country, 1)
        self.assertContains(self.response, target_html_object_count, 1)
        self.assertContains(self.response, target_html_object_percentage, 1)


class TestMapMetricsWithStatistics(TestCase):
    """
    Test html render map metrics if statistics exists.
    """

    def setUp(self):
        """
        Run setup. Provide common response.
        """
        SetUp.setUp()
        self.response = self.client.get('/map/')

    def test_top_country(self):
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

        self.assertContains(self.response, target_html_object, 1)

    def test_countries_amount(self):
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

        self.assertContains(self.response, target_html_object, 1)

    def test_counties_accordance(self):
        """
        Verify that html renders table with all accordance to geographic table if students country statistics exists.
        """
        installation_statistics = InstallationStatistics()

        factory_students_per_country_accordance = json.loads(InstallationStatisticsFactory.students_per_country)

        all_active_students = sum(factory_students_per_country_accordance.values())

        for country, count in factory_students_per_country_accordance.items():
            if installation_statistics.does_country_exists(country):

                student_amount_percentage = installation_statistics.get_student_amount_percentage(
                    count, all_active_students
                )

                country_alpha_3 = str(
                    pycountry.countries.get(alpha_2=country).alpha_3
                )

                target_html_object_country = html_target.country_grid_cell.format(country_alpha_3)
                target_html_object_count = html_target.country_count_grid_cell.format(count)
                target_html_object_percentage = html_target.percentage_grid_cell.format(student_amount_percentage)

                self.assertContains(self.response, target_html_object_country, 1)
                self.assertContains(self.response, target_html_object_count, 1)
                self.assertContains(self.response, target_html_object_percentage, 1)
