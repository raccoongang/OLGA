import json
from datetime import datetime

from mock import patch, Mock

from django.test import TestCase

from olga.charts.views import (
    MapView,
    get_first_and_last_datetime_of_update_data
)


class TestMapView(TestCase):

    def test_map_url_resolves_to_map_view(self):
        response = self.client.get('/map/')

        self.assertEqual(response.resolver_match.func.__name__, MapView.__name__)

    def test_map_view_get_returns_status_code_ok(self):
        response = self.client.get('/map/')

        self.assertEqual(response.status_code, 200)

    def test_map_view_get_returns_correct_html(self):
        response = self.client.get('/map/')

        self.assertTemplateUsed(response, 'charts/worldmap.html')

    def test_map_view_get_returns_correct_view_context_fields(self):
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

        tabular_format_countries_list = [['Canada', 66, '20'], ['United States', 33, '10']]

        result = MapView.get_statistics_top_country(tabular_format_countries_list)

        self.assertEqual('Canada', result)

    def test_get_statistics_top_country_returns_mone_if_tabular_format_countries_list_is_empty(self):

        tabular_format_countries_list = []

        result = MapView.get_statistics_top_country(tabular_format_countries_list)

        self.assertEqual(None, result)

    @patch('olga.analytics.models.InstallationStatistics.objects.last')
    @patch('olga.analytics.models.InstallationStatistics.objects.first')
    def test_get_first_and_last_datetime_of_update_data_returns_objects_datetime_if_it_exists(
            self,
            mock_installation_statistics_model_objects_first_method,
            mock_installation_statistics_model_objects_last_method
    ):
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

        mock_installation_statistics_model_objects_first_method.side_effect = AttributeError()

        mock_first_datetime_of_update_data = mock_last_datetime_of_update_data = datetime(2017, 7, 2, 23, 12, 8)

        mock_datetime.now.return_value = mock_first_datetime_of_update_data

        result = get_first_and_last_datetime_of_update_data()

        print(mock_datetime)

        self.assertEqual(
            (mock_first_datetime_of_update_data, mock_last_datetime_of_update_data), result
        )
