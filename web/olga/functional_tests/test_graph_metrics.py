"""
Test for graphs metrics.
"""

from ddt import ddt, data, unpack

from django.test import TestCase

from olga.analytics.tests.factories import InstallationStatisticsFactory
from olga.functional_tests.utils import SetUp, html_target

# pylint: disable=invalid-name, attribute-defined-outside-init


factory_stats = InstallationStatisticsFactory()


@ddt
class TestGraphsMetricsWithoutStatistics(TestCase):
    """
    Test html render graphs metrics if statistics does not exist.
    """

    @data([0, 'Instances'], [None, 'Courses'], [None, 'Active Students'])
    @unpack
    def test_activity_metrics_if_no_statistics(self, amount, label):
        """
        Verify that html renders zero (0) to instance activity metric if no instance amount for last calendar day.
        """
        response = self.client.get('/')

        target_html_object = html_target.activity_metric.format(amount, label)

        self.assertContains(response, target_html_object, 1)


@ddt
class TestMapMetricsWithStatistics(TestCase):
    """
    Test html render graphs metrics if statistics exists.
    """

    def setUp(self):
        """
        Run setup. Provide common response.
        """
        SetUp.setUp()
        self.response = self.client.get('/')

    @data(
        [1, 'Instances'],
        [factory_stats.courses_amount, 'Courses'],
        [factory_stats.active_students_amount_day, 'Active Students']
    )
    @unpack
    def test_metrics(self, amount, label):
        """
        Verify that html renders instances, courses and students amount to corresponding activity metrics.

        About ddt`s data: without using unpack values code generates duplicate issues.
        Here is no way to set that data automatically:
            - result of outside functions (i.e. `overall_counts` method) can't be passed to `data`;
            - self can't be passed to `data`.

        Resolved problem with manually setting values, that factory provides.
        """
        target_html_object = html_target.activity_metric.format(amount, label)
        self.assertContains(self.response, target_html_object, 1)
