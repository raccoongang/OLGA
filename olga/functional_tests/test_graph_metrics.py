"""
Test for graphs metrics.
"""

from django.test import TestCase

from ddt import ddt, data, unpack

from olga.functional_tests.utils import SetUp, html_target

from olga.analytics.models import InstallationStatistics

# pylint: disable=invalid-name, attribute-defined-outside-init


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

    @staticmethod
    def get_overall_counts():
        """
        Return instances, courses and students amounts as tuple.
        """
        return InstallationStatistics.overall_counts()

    def test_instance_metric(self):
        """
        Verify that html renders instances amount to instances activity metric if statistics statistics.

        Instances amount is a total, that compiled from all objects for last calendar day.
        """
        instances_amount, _, __ = self.get_overall_counts()
        instances_label = 'Instances'

        target_html_object = html_target.activity_metric.format(
            instances_amount, instances_label
        )

        self.assertContains(self.response, target_html_object, 1)

    def test_courses_metric(self):
        """
        Verify that html renders courses amount to courses activity metric if statistics statistics.

        Courses amount is a total, that compiled from all objects for last calendar day.
        """
        _, courses_amount, __ = self.get_overall_counts()
        courses_label = 'Courses'

        target_html_object = html_target.activity_metric.format(
            courses_amount, courses_label
        )

        self.assertContains(self.response, target_html_object, 1)

    def test_students_metric(self):
        """
        Verify that html renders students amount to students activity metric if statistics statistics.

        Students amount is a total, that compiled from all objects for last calendar day.
        """
        _, __, active_students_amount = self.get_overall_counts()
        active_students_label = 'Active Students'

        target_html_object = html_target.activity_metric.format(
            active_students_amount, active_students_label
        )

        self.assertContains(self.response, target_html_object, 1)
