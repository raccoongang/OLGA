"""
Tests for charts views.
"""

import json
from datetime import datetime

from mock import patch, Mock

from django.test import TestCase

from olga.charts.views import (
    MapView,
    GraphsView,
    get_first_and_last_datetime_of_update_data
)


class TestMapView(TestCase):
    """
    Tests for map view, that contains world map statistics functionality.
    """

    def test_map_url_resolves_to_map_view(self):
        """
        Verifies that map url resolves to map view.
        """
        response = self.client.get('/map/')

        self.assertEqual(response.resolver_match.func.__name__, MapView.__name__)

    def test_map_view_get_returns_status_code_ok(self):
        """
        Verifies that map view returns status 200 (ok) after get request to map url.
        """

        response = self.client.get('/map/')

        self.assertEqual(response.status_code, 200)

    def test_map_view_get_uses_correct_html(self):
        """
        Verifies that map view uses correct html-template after get request to map url.
        """

        response = self.client.get('/map/')

        self.assertTemplateUsed(response, 'charts/worldmap.html')

    def test_map_view_get_render_correct_view_context_fields(self):
        """
        Verifies that map view render correct context fields.
        """

        response = self.client.get('/map/')

        context_fields = [
            'datamap_countries_list',
            'tabular_countries_list',
            'top_country',
            'countries_amount',
            'first_datetime_of_update_data',
            'last_datetime_of_update_data',
        ]

        for field in context_fields:
            self.assertIn(field, response.context)

    @patch('olga.charts.views.MapView.get_statistics_top_country')
    @patch('olga.analytics.models.InstallationStatistics.get_worlds_students_per_country_data_to_render')
    @patch('olga.charts.views.get_first_and_last_datetime_of_update_data')
    def test_map_view_get_returns_correct_view_context_fields_values(
            self,
            mock_get_first_and_last_datetime_of_update_data,
            mock_get_worlds_students_per_country_data_to_render,
            mock_get_statistics_top_country
    ):
        """
        Verifies that map view render correct context fields values.
        """

        mock_countries_amount, mock_datamap_format_countries_list, mock_tabular_format_countries_list = \
            10, [['US', '10'], ['CA', '20']], [['Canada', 66, '20'], ['United States', 33, '10']]

        mock_first_datetime_of_update_data, mock_last_datetime_of_update_data = \
            datetime(2017, 6, 1, 14, 56, 18), datetime(2017, 7, 2, 23, 12, 8)

        top_country = 'Canada'

        mock_get_first_and_last_datetime_of_update_data.return_value = (
            mock_first_datetime_of_update_data, mock_last_datetime_of_update_data
        )

        mock_get_worlds_students_per_country_data_to_render.return_value = (
            mock_countries_amount, mock_datamap_format_countries_list, mock_tabular_format_countries_list
        )

        mock_get_statistics_top_country.return_value = top_country

        response = self.client.get('/map/')

        self.assertEqual(json.loads(response.context['datamap_countries_list']), mock_datamap_format_countries_list)
        self.assertEqual(response.context['tabular_countries_list'], mock_tabular_format_countries_list)
        self.assertEqual(response.context['top_country'], top_country)
        self.assertEqual(response.context['countries_amount'], mock_countries_amount)
        self.assertEqual(response.context['first_datetime_of_update_data'], mock_first_datetime_of_update_data)
        self.assertEqual(response.context['last_datetime_of_update_data'], mock_last_datetime_of_update_data)

    def test_get_statistics_top_country_returns_top_country_if_tabular_format_countries_list_exists(self):
        """
        Verifies that get_statistics_top_country method returns top country if tabular format countries list exists.

        Actually before using get_statistics_top_country method server sorts tabular format countries list
        in descending order, that means first element is top value.
        """

        tabular_format_countries_list = [['Canada', 66, '20'], ['United States', 33, '10']]

        result = MapView.get_statistics_top_country(tabular_format_countries_list)

        self.assertEqual('Canada', result)

    def test_get_statistics_top_country_returns_none_if_tabular_format_countries_list_is_empty(self):
        """
        Verifies that get_statistics_top_country method returns non if tabular format countries list is empty.
        """

        tabular_format_countries_list = []

        result = MapView.get_statistics_top_country(tabular_format_countries_list)

        self.assertEqual(None, result)


class TestViewsUtils(TestCase):

    @patch('olga.analytics.models.InstallationStatistics.objects.last')
    @patch('olga.analytics.models.InstallationStatistics.objects.first')
    def test_get_first_and_last_datetime_of_update_data_returns_objects_datetime_if_it_exists(
            self,
            mock_installation_statistics_model_objects_first_method,
            mock_installation_statistics_model_objects_last_method
    ):
        """
        Verifies that get_first_and_last_datetime_of_update_data method returns first object datetime and
        last object datetime in database.
        """

        mock_first_datetime_of_update_data = datetime(2017, 6, 1, 14, 56, 18)
        mock_last_datetime_of_update_data = datetime(2017, 7, 2, 23, 12, 8)

        class MockInstallationStatisticsModelFirstObject:
            data_created_datetime = mock_first_datetime_of_update_data

        class MockInstallationStatisticsModelLastObject:
            data_created_datetime = mock_last_datetime_of_update_data

        mock_installation_statistics_model_objects_first_method.return_value = \
            MockInstallationStatisticsModelFirstObject()

        mock_installation_statistics_model_objects_last_method.return_value = \
            MockInstallationStatisticsModelLastObject()

        result = get_first_and_last_datetime_of_update_data()

        self.assertEqual(
            (mock_first_datetime_of_update_data, mock_last_datetime_of_update_data), result
        )

    @patch('olga.charts.views.datetime')
    @patch('olga.analytics.models.InstallationStatistics.objects.first')
    def test_get_first_and_last_datetime_of_update_data_returns_datetime_now_if_objects_datetime_does_not_exist(
            self, mock_installation_statistics_model_objects_first_method, mock_datetime
    ):
        """
        Verifies that get_first_and_last_datetime_of_update_data method returns `datetime.now` if first object datetime
        and last object datetime do not exist in database.
        """

        mock_installation_statistics_model_objects_first_method.side_effect = AttributeError()

        mock_first_datetime_of_update_data = mock_last_datetime_of_update_data = datetime(2017, 7, 2, 23, 12, 8)

        mock_datetime.now.return_value = mock_first_datetime_of_update_data

        result = get_first_and_last_datetime_of_update_data()

        self.assertEqual(
            (mock_first_datetime_of_update_data, mock_last_datetime_of_update_data), result
        )


class TestGraphsView(TestCase):
    """
    Tests for map view, that contains graphs statistics functionality.
    """

    def test_graphs_url_resolves_to_map_view(self):
        """
        Verifies that graphs url resolves to graphs view.
        """
        response = self.client.get('/')

        self.assertEqual(response.resolver_match.func.__name__, GraphsView.__name__)

    def test_graphs_view_get_returns_status_code_ok(self):
        """
        Verifies that graphs view returns status 200 (ok) after get request to graphs url.
        """

        response = self.client.get('/')

        self.assertEqual(response.status_code, 200)

    def test_graphs_view_get_uses_correct_html(self):
        """
        Verifies that graphs view uses correct html-template after get request to graphs url.
        """

        response = self.client.get('/')

        self.assertTemplateUsed(response, 'charts/graphs.html')

    def test_graphs_view_get_render_correct_view_context_fields(self):
        """
        Verifies that graphs view render correct context fields.
        """

        response = self.client.get('/')

        context_fields = [
            'timeline',
            'students',
            'courses',
            'instances',
            'instances_count',
            'courses_count',
            'students_count',
            'first_datetime_of_update_data',
            'last_datetime_of_update_data'
        ]

        for field in context_fields:
            self.assertIn(field, response.context)

    @patch('olga.charts.views.get_first_and_last_datetime_of_update_data')
    @patch('olga.analytics.models.InstallationStatistics.timeline')
    @patch('olga.analytics.models.InstallationStatistics.data_per_period')
    @patch('olga.analytics.models.InstallationStatistics.overall_counts')
    def test_map_view_get_returns_correct_view_context_fields_values(
            self,
            mock_installation_statistics_model_overall_counts,
            mock_installation_statistics_model_data_per_period,
            mock_installation_statistics_model_timeline,
            mock_get_first_and_last_datetime_of_update_data
    ):
        """
        Verifies that graphs view render correct context fields values.
        """

        mock_timeline = ['2017-05-14', '2017-05-15', '2017-05-16']
        mock_students, mock_courses, mock_instances = [4124, 5122, 6412], [110, 211, 167], [30, 20, 25]
        mock_instances_count, mock_courses_count, mock_students_count = 6412, 167, 25
        mock_first_datetime_of_update_data = datetime(2017, 6, 1, 14, 56, 18)
        mock_last_datetime_of_update_data = datetime(2017, 7, 2, 23, 12, 8)

        mock_installation_statistics_model_timeline.return_value = mock_timeline

        mock_installation_statistics_model_data_per_period.return_value = mock_students, mock_courses, mock_instances

        mock_installation_statistics_model_overall_counts.return_value = \
            mock_instances_count, mock_courses_count, mock_students_count

        mock_get_first_and_last_datetime_of_update_data.return_value = \
            mock_first_datetime_of_update_data, mock_last_datetime_of_update_data

        response = self.client.get('/')

        self.assertEqual(json.loads(response.context['timeline']), mock_timeline)
        self.assertEqual(json.loads(response.context['students']), mock_students)
        self.assertEqual(json.loads(response.context['courses']), mock_courses)
        self.assertEqual(json.loads(response.context['instances']), mock_instances)
        self.assertEqual(response.context['instances_count'], mock_instances_count)
        self.assertEqual(response.context['students_count'], mock_students_count)
        self.assertEqual(response.context['courses_count'], mock_courses_count)
        self.assertEqual(response.context['first_datetime_of_update_data'], mock_first_datetime_of_update_data)
        self.assertEqual(response.context['last_datetime_of_update_data'], mock_last_datetime_of_update_data)
