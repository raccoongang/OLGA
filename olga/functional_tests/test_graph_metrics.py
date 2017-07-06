"""
Test for graphs metrics.
"""

from django.test import TestCase

from olga.functional_tests.utils import SetUp, html_target

from olga.analytics.models import InstallationStatistics

# pylint: disable=invalid-name


class TestGraphsMetricsWithoutStatistics(TestCase):
    """
    Test html render graphs metrics if statistics does not exist.
    """

    def test_html_renders_zero_to_instance_activity_metric_if_no_instances(self):
        """
        Verify that html renders zero (0) to instance activity metric if no instance amount for last calendar day.
        """
        response = self.client.get('/')

        instances_amount = 0
        instances_label = 'Instances'

        # print('<<', HtmlTargets.activity_metric_html_target)
        # print(dir(HtmlTargets.activity_metric_html_target))

        target_html_object = html_target.activity_metric.format(
            instances_amount, instances_label
        )

        self.assertContains(response, target_html_object, 1)

    def test_html_renders_none_to_courses_activity_metric_if_no_courses(self):
        """
        Verify that html renders None to courses activity metric if no courses amount for last calendar day.
        """
        response = self.client.get('/')

        courses_amount = None
        courses_label = 'Courses'

        target_html_object = html_target.activity_metric.format(
            courses_amount, courses_label
        )

        self.assertContains(response, target_html_object, 1)

    def test_html_renders_none_to_students_activity_metric_if_no_students(self):
        """
        Verify that html renders None to students activity metric if no students amount for last calendar day.
        """
        response = self.client.get('/')

        active_students_amount = None
        active_students_label = 'Active Students'

        target_html_object = html_target.activity_metric.format(
            active_students_amount, active_students_label
        )

        self.assertContains(response, target_html_object, 1)


class TestMapMetricsWithStatistics(TestCase):
    """
    Test html render graphs metrics if statistics exists.
    """

    @staticmethod
    def setUp():
        """
        Run setup.
        """
        SetUp.setUp()

    @staticmethod
    def get_overall_counts():
        """
        Return instances, courses and students amounts as tuple.
        """
        return InstallationStatistics.overall_counts()

    def test_html_renders_instances_amount_to_instance_activity_metric_if_statistics_exists(self):
        """
        Verify that html renders instances amount to instances activity metric if statistics statistics.

        Instances amount is a total, that compiled from all objects for last calendar day.
        """
        response = self.client.get('/')

        instances_amount, _, __ = self.get_overall_counts()
        instances_label = 'Instances'

        target_html_object = html_target.activity_metric.format(
            instances_amount, instances_label
        )

        self.assertContains(response, target_html_object, 1)

    def test_html_renders_courses_amount_to_courses_activity_metric_if_statistics_exists(self):
        """
        Verify that html renders courses amount to courses activity metric if statistics statistics.

        Courses amount is a total, that compiled from all objects for last calendar day.
        """
        response = self.client.get('/')

        _, courses_amount, __ = self.get_overall_counts()
        courses_label = 'Courses'

        target_html_object = html_target.activity_metric.format(
            courses_amount, courses_label
        )

        self.assertContains(response, target_html_object, 1)

    def test_html_renders_students_amount_to_students_activity_metric_if_statistics_exists(self):
        """
        Verify that html renders students amount to students activity metric if statistics statistics.

        Students amount is a total, that compiled from all objects for last calendar day/
        """
        response = self.client.get('/')

        _, __, active_students_amount = self.get_overall_counts()
        active_students_label = 'Active Students'

        target_html_object = html_target.activity_metric.format(
            active_students_amount, active_students_label
        )

        self.assertContains(response, target_html_object, 1)
