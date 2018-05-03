"""
Test for map metrics.
"""

from ddt import ddt, data, unpack

from django.test import TestCase

from olga.functional_tests.utils import SetUp, html_target

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

    @data(
        ['', 'Top Country by Enrollment', 'top_country'],
        ['', 'Countries in Statistics', 'countries_amount']
    )
    @unpack
    def test_unset_country(self, value, label, element_id):
        """
        Verify that html renders unset to country activity metric if no students country.
        """
        target_html_object = html_target.activity_metric_with_id(element_id).format(value, label)

        self.assertContains(self.response, target_html_object, 1)


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
        Verify that html renders top country element to activity metric.
        """
        max_students_country_alpha_3_label = 'Top Country by Enrollment'

        target_html_object = html_target.activity_metric_with_id('top_country').format(
            '', max_students_country_alpha_3_label
        )

        self.assertContains(self.response, target_html_object, 1)

    def test_countries_amount(self):
        """
        Verify that html renders countries amount element to activity metric.
        """
        countries_in_statistics_label = 'Countries in Statistics'

        target_html_object = html_target.activity_metric_with_id('countries_amount').format(
            '', countries_in_statistics_label
        )

        self.assertContains(self.response, target_html_object, 1)
