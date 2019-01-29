"""
Tests for analytics utils.
"""

import http.client as http
import unittest

from mock import call, patch

from django.http import HttpResponse
from django.test import TestCase
from django.test.client import RequestFactory

from olga.analytics.utils import get_coordinates_by_platform_city_name, validate_instance_stats_forms

# pylint: disable=invalid-name, attribute-defined-outside-init, protected-access


class TestInstallationStatisticsFormsChecker(TestCase):
    """
    Tests for installation statistics forms checker decorator.
    """

    def setUp(self):
        """
        Provide basic action and common variables as passing method to decorator (it is not intended for testing).
        """
        factory_request = RequestFactory()
        self.factory_request = factory_request

        self.factory_request_post = factory_request.post('/api/installation/statistics/', {'kwargs': 'kwargs'})
        self.fake_response = 'fake_response'

        with patch('olga.analytics.views.ReceiveInstallationStatistics.post') as self.mock_decorated_method:
            self.mock_decorated_method.return_value = self.fake_response

        self.decorator_wrapper = validate_instance_stats_forms(self.mock_decorated_method)

    def change_query_dict(self, key, value):
        """
        Change request post kwarg.
        """
        self.factory_request_post.POST._mutable = True
        self.factory_request_post.POST[key] = value
        self.factory_request_post.POST._mutable = False

    @patch('olga.analytics.forms.EdxInstallationParanoidLevelForm.is_valid')
    @patch('olga.analytics.forms.InstallationStatisticsParanoidLevelForm.is_valid')
    def test_paranoid_level_forms_are_valid(self, mock_paranoid_installation_form, mock_paranoid_statistics_form):
        """
        Verify, that installation_statistics_forms_checker decorator returns correct result if forms are valid.
        """
        mock_paranoid_installation_form.return_value = mock_paranoid_statistics_form.return_value = True

        self.change_query_dict('statistics_level', 'paranoid')

        self.decorator_wrapper_response = self.decorator_wrapper(self.factory_request_post)
        self.assertEqual(self.fake_response, self.decorator_wrapper_response)

    @patch('olga.analytics.forms.EdxInstallationParanoidLevelForm.is_valid')
    @patch('olga.analytics.forms.InstallationStatisticsParanoidLevelForm.is_valid')
    def test_paranoid_level_forms_are_not_valid(self, mock_paranoid_installation_form, mock_paranoid_statistics_form):
        """
        Verify, that installation_statistics_forms_checker decorator returns correct result if forms are not valid.
        """
        mock_paranoid_installation_form.return_value = mock_paranoid_statistics_form.return_value = False

        self.change_query_dict('statistics_level', 'paranoid')

        self.decorator_wrapper_response = self.decorator_wrapper(self.factory_request_post)

        self.assertEqual(http.UNAUTHORIZED, self.decorator_wrapper_response.status_code)
        self.assertEqual(HttpResponse, self.decorator_wrapper_response.__class__)

    @patch('olga.analytics.forms.EdxInstallationEnthusiastLevelForm.is_valid')
    @patch('olga.analytics.forms.InstallationStatisticsEnthusiastLevelForm.is_valid')
    def test_enthusiast_level_forms_are_valid(self, mock_enthusiast_installation_form, mock_enthusiast_statistics_form):
        """
        Verify, that installation_statistics_forms_checker decorator returns correct result if forms are valid.
        """
        mock_enthusiast_installation_form.return_value = mock_enthusiast_statistics_form.return_value = True

        self.change_query_dict('statistics_level', 'enthusiast')

        self.decorator_wrapper_response = self.decorator_wrapper(self.factory_request_post)
        self.assertEqual(self.fake_response, self.decorator_wrapper_response)

    @patch('olga.analytics.forms.EdxInstallationEnthusiastLevelForm.is_valid')
    @patch('olga.analytics.forms.InstallationStatisticsEnthusiastLevelForm.is_valid')
    def test_enthusiast_level_forms_are_not_valid(
            self, mock_enthusiast_installation_form, mock_enthusiast_statistics_form
    ):
        """
        Verify, that installation_statistics_forms_checker decorator returns correct result if forms are not valid.
        """
        mock_enthusiast_installation_form.return_value = mock_enthusiast_statistics_form.return_value = False

        self.change_query_dict('statistics_level', 'enthusiast')

        self.decorator_wrapper_response = self.decorator_wrapper(self.factory_request_post)

        self.assertEqual(http.UNAUTHORIZED, self.decorator_wrapper_response.status_code)
        self.assertEqual(HttpResponse, self.decorator_wrapper_response.__class__)

    @patch('olga.analytics.forms.EdxInstallationParanoidLevelForm.is_valid')
    @patch('olga.analytics.forms.InstallationStatisticsParanoidLevelForm.is_valid')
    def test_decorated_method_if_forms_are_valid(self, mock_paranoid_installation_form, mock_paranoid_statistics_form):
        """
        Verify, that decorated REST method called once with corresponding request, agrs and kwargs.
        """
        mock_paranoid_installation_form.return_value = mock_paranoid_statistics_form.return_value = True

        self.change_query_dict('statistics_level', 'paranoid')

        self.decorator_wrapper(self.factory_request_post)
        self.mock_decorated_method.assert_called_once_with(self.factory_request_post)


@patch('olga.analytics.utils.requests.get')
class TestPlatformCoordinates(unittest.TestCase):
    """
    Test for platform coordinates method, that gather latitude and longitude.
    """

    def tests_sending_requests(self, mock_request):
        """
        Test to prove that method send request to needed corresponding URL.
        """
        # Verify that get_coordinates_by_platform_city_name sends request to API with address as parameter.
        get_coordinates_by_platform_city_name('Kiev')

        expected_calls = [
            call('https://nominatim.openstreetmap.org/search/', params={'city': 'Kiev', 'format': 'json'}),
        ]

        self.assertEqual(mock_request.call_args_list, expected_calls)

    def test_platform_city_name_if_wrong_city_name(self, mock_request):
        """
        Verify that get_coordinates_by_platform_city_name returns None if platform city name in settings is wrong.
        """
        mock_request.return_value.json.return_value = {'results': []}

        result_without_city_name = get_coordinates_by_platform_city_name('Lmnasasfabqwrqrn')
        self.assertEqual(('', ''), result_without_city_name)
