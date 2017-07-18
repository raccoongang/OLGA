"""
Test for output dates.
"""

from datetime import datetime

from django.test import TestCase

from olga.functional_tests.utils import SetUp, html_target

from olga.charts.views import get_first_and_last_datetime_of_update_data

# pylint: disable=invalid-name, attribute-defined-outside-init


class TestHtmlRenderDatesWithoutData(TestCase):
    """
    Test html render dates if statistics does not exist.
    """

    def test_datetime_now_if_no_statistics(self):
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

    def test_last_update_if_no_students_country(self):
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

    def setUp(self):
        """
        Run setup. Provide common response.
        """
        SetUp.setUp()
        self.response = self.client.get('/map/')

        first_datetime_of_update_data, last_datetime_of_update_data = get_first_and_last_datetime_of_update_data()

        self.first_update_date_y_m = first_datetime_of_update_data.strftime('%Y-%m')
        self.last_update_date_y_m = last_datetime_of_update_data.strftime('%Y-%m')

        self.first_update_date_y_m_d = last_datetime_of_update_data.strftime('%Y-%m-%d')
        self.last_update_time_h_m = last_datetime_of_update_data.strftime('%H:%M')

    def test_existing_datetime(self):
        """
        Verify that statistics extraction duration uses first and last data update datetime if statistics exists.
        """
        self.assertContains(
            self.response,
            html_target.extraction_duration.format(self.first_update_date_y_m, self.last_update_date_y_m),
            1
        )

    def test_last_update(self):
        """
        Verify that html renders first and last data update datetime for course engagement dates if statistics exists.
        """
        self.assertContains(
            self.response,
            html_target.course_engagement_last_update.format(self.first_update_date_y_m_d, self.last_update_time_h_m),
            1
        )
