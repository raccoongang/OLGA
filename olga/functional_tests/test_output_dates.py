

"""
Test for output dates.
"""

from datetime import datetime

from django.test import TestCase

from olga.functional_tests.utils import SetUp, html_target

from olga.charts.views import get_first_and_last_datetime_of_update_data

# pylint: disable=invalid-name


class TestHtmlRenderDatesWithoutData(TestCase):
    """
    Test html render dates if statistics does not exist.
    """

    def test_statistics_extraction_duration_uses_datetime_now_duration_if_no_statistics(self):
        """
        Verify that statistics extraction duration uses datetime now if no statistics.
        """
        first_update_strftime_date = last_update_strftime_date = datetime.now().strftime('%Y-%m')

        response = self.client.get('/map/')

        self.assertContains(
            response,
            html_target.extraction_duration.format(first_update_strftime_date, last_update_strftime_date),
            1
        )

    def test_course_engagement_data_was_last_updated_if_no_students_country(self):
        """
        Verify that html renders datetime now for course engagement data was last updated if no statistics.
        """
        last_update_strftime_date = datetime.now().strftime('%Y-%m-%d')
        last_update_strftime_time = datetime.now().strftime('%H:%M')

        response = self.client.get('/map/')

        self.assertContains(
            response,
            html_target.course_engagement_last_update.format(last_update_strftime_date, last_update_strftime_time),
            1
        )


class TestHtmlRenderDatesWithData(TestCase):
    """
    Test html render dates if statistics exists.
    """

    @staticmethod
    def setUp():
        """
        Run setup.
        """
        SetUp.setUp()

    def test_statistics_extraction_duration_uses_existing_datetime_if_statistics_exists(self):
        """
        Verify that statistics extraction duration uses first and last data update datetime if statistics exists.
        """
        first_datetime_of_update_data, last_datetime_of_update_data = get_first_and_last_datetime_of_update_data()

        first_update_strftime_date = first_datetime_of_update_data.strftime('%Y-%m')
        last_update_strftime_date = last_datetime_of_update_data.strftime('%Y-%m')

        response = self.client.get('/map/')

        self.assertContains(
            response,
            html_target.extraction_duration.format(first_update_strftime_date, last_update_strftime_date),
            1
        )

    def test_course_engagement_data_was_last_updated_uses_existing_datetime_if_statistics_exists(self):
        """
        Verify that html renders first and last data update datetime for course engagement dates if statistics exists.
        """
        _, last_datetime_of_update_data = get_first_and_last_datetime_of_update_data()

        last_update_strftime_date = last_datetime_of_update_data.strftime('%Y-%m-%d')
        last_update_strftime_time = last_datetime_of_update_data.strftime('%H:%M')

        response = self.client.get('/map/')

        self.assertContains(
            response,
            html_target.course_engagement_last_update.format(last_update_strftime_date, last_update_strftime_time),
            1
        )
