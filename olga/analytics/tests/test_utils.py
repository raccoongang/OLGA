"""
Tests for analytics utils.
"""

import httplib

from mock import patch

from django.test import TestCase

from django.http import HttpResponse

from olga.analytics.utils import validate_instance_stats_forms

# pylint: disable=invalid-name, attribute-defined-outside-init


@patch('olga.analytics.forms.InstallationStatisticsForm.is_valid')
@patch('olga.analytics.forms.EdxInstallationForm.is_valid')
class TestInstallationStatisticsFormsChecker(TestCase):
    """
    Tests for installation statistics forms checker decorator.
    """

    def setUp(self):
        """
        Provide basic action and common variables as passing method to decorator (it is not intended for testing).
        """
        class Request(object):  # pylint: disable=too-few-public-methods
            """
            Interface for mocking and faking request.
            """

            POST, args, kwargs = {}, ('args', ), {'kwargs': 'kwargs'}

        self.request = Request()
        self.fake_response = 'fake_response'

        with patch('olga.analytics.views.ReceiveInstallationStatistics.post') as self.mock_decorated_method:
            self.mock_decorated_method.return_value = self.fake_response

        self.decorator_wrapper = validate_instance_stats_forms(self.mock_decorated_method)

    def test_decorator_if_forms_are_valid(
            self, mock_edx_installation_form, mock_installation_statistics_form
    ):
        """
        Verify, that installation_statistics_forms_checker decorator returns correct result if forms are valid.
        """
        mock_installation_statistics_form.return_value = mock_edx_installation_form.return_value = True

        self.decorator_wrapper_response = self.decorator_wrapper(
            self.request, *self.request.args, **self.request.kwargs
        )

        self.assertEqual(self.fake_response, self.decorator_wrapper_response)

    def test_decorator_if_forms_are_not_valid(
            self, mock_edx_installation_form, mock_installation_statistics_form
    ):
        """
        Verify, that installation_statistics_forms_checker decorator returns correct result if forms are not valid.
        """
        mock_edx_installation_form.return_value = mock_installation_statistics_form.return_value = False

        self.decorator_wrapper_response = self.decorator_wrapper(
            self.request, *self.request.args, **self.request.kwargs
        )

        self.assertEqual(httplib.UNAUTHORIZED, self.decorator_wrapper_response.status_code)
        self.assertEqual(HttpResponse, self.decorator_wrapper_response.__class__)

    def test_decorated_method_if_forms_are_valid(
            self, mock_edx_installation_form, mock_installation_statistics_form
    ):
        """
        Verify, that decorated REST method called once with corresponding request, agrs and kwargs.
        """
        mock_installation_statistics_form.return_value = mock_edx_installation_form.return_value = True

        self.decorator_wrapper(self.request, *self.request.args, **self.request.kwargs)
        self.mock_decorated_method.assert_called_once_with(self.request, *self.request.args, **self.request.kwargs)
