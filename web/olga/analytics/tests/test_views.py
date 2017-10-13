"""
Tests for analytics views.
"""

import copy
import httplib
import json
import uuid
from datetime import datetime, timedelta

from mock import patch, call

from django.http import HttpResponse, QueryDict
from django.test import TestCase
from django.utils.encoding import force_text
from django.utils.crypto import get_random_string

from olga.analytics.models import EdxInstallation, InstallationStatistics
from olga.analytics.tests.factories import EdxInstallationFactory

from olga.analytics.views import (
    AccessTokenAuthorization,
    AccessTokenRegistration,
    ReceiveInstallationStatistics
)


# pylint: disable=invalid-name


class MockUUID4(object):  # pylint: disable=too-few-public-methods
    """
    Mock UUID4 hex value.

    It is needed while mock can't fake uuid4 hex value correctly.
    Mock raises ValueError with F() expressions can only be used to update, not to insert.
    """

    access_token = uuid.uuid4().hex
    hex = access_token


class InstallationDefaultData(object):  # pylint: disable=too-few-public-methods
    """
    Provide default data that uses in edx installation and Acceptor server flow.
    """

    @staticmethod
    def create_installation_default_data():
        """
        Create default data that uses in edx installation and Acceptor server flow.
        """
        received_data = {
            'access_token': '5cc8d820-cece-49c2-b3a6-17e135c771fb',
            'active_students_amount_day': '10',
            'active_students_amount_week': '15',
            'active_students_amount_month': '20',
            'courses_amount': '10',
            'latitude': '50.10',
            'longitude': '40.50',
            'platform_name': 'platform_name',
            'platform_url': 'https://platform.url',
            'statistics_level': 'enthusiast',
            'students_per_country': "{\"RU\": 10, \"CA\": 5, \"UA\": 20}"
        }

        installation_statistics = {
            'active_students_amount_day': 10,
            'active_students_amount_week': 15,
            'active_students_amount_month': 20,
            'courses_amount': 10,
            'statistics_level': 'enthusiast'
        }

        enthusiast_edx_installation = {
            'latitude': 50.10,
            'longitude': 40.50,
            'platform_name': 'platform_name',
            'platform_url': 'https://platform.url'
        }

        return received_data, installation_statistics, enthusiast_edx_installation


class TestAccessTokenRegistration(TestCase):
    """
    Tests for access token registration.
    """

    def test_get_access_token_for_uid(self):
        """
        Verify that new installation created after call of get_access_token_for_uid call.
        """
        uid = get_random_string()
        AccessTokenRegistration().get_access_token_for_uid(uid)

        self.assertEqual(1, EdxInstallation.objects.all().count())

    def test_get_access_token_for_uid_double_with_same_uid(self):
        """
        Verify that only one new installation create after double call of get_access_token_for_uid call with same uid.
        """
        uid = get_random_string()
        AccessTokenRegistration().get_access_token_for_uid(uid)
        AccessTokenRegistration().get_access_token_for_uid(uid)

        self.assertEqual(1, EdxInstallation.objects.all().count())

    def test_get_access_token_for_uid_double_with_different_uid(self):
        """
        Verify that two new installations are created after double get_access_token_for_uid call with different uid.
        """
        uid = get_random_string()
        AccessTokenRegistration().get_access_token_for_uid(uid)
        uid = get_random_string()
        AccessTokenRegistration().get_access_token_for_uid(uid)

        self.assertEqual(2, EdxInstallation.objects.all().count())

    @patch('olga.analytics.views.uuid4')
    def test_post_method(self, mock_uuid4):
        """
        Test post method response.
        """
        mock_uuid4.return_value = MockUUID4()

        response = self.client.post('/api/token/registration/', {'uid': get_random_string()})

        self.assertEqual(response.status_code, httplib.CREATED)
        self.assertJSONEqual(
            force_text(response.content),
            {'access_token': mock_uuid4.return_value.access_token}
        )

    @patch('olga.analytics.views.uuid4')
    def test_post_method_without_uid(self, mock_uuid4):
        """
        Test post method response from registration endpoint without uid.
        """
        mock_uuid4.return_value = MockUUID4()

        response = self.client.post('/api/token/registration/', {})

        self.assertEqual(response.status_code, httplib.BAD_REQUEST)

    @patch('olga.analytics.views.AccessTokenRegistration.get_access_token_for_uid', )
    def test_get_access_token_for_uid_occurs(
            self, get_access_token_for_uid
    ):
        """
        Test get_access_token_for_uid method accepts uid during post method`s process.
        """
        get_access_token_for_uid.return_value = uuid.uuid4().hex
        uid = get_random_string()

        self.client.post('/api/token/registration/', {'uid': uid})

        get_access_token_for_uid.assert_called_once_with(uid)

    @patch('olga.analytics.views.logging.Logger.debug')
    @patch('olga.analytics.views.uuid4')
    def test_logger_debug_occurs(self, mock_uuid4, mock_logger_debug):
        """
        Test logger`s debug output during post method`s process.
        """
        mock_uuid4.return_value = MockUUID4()

        uid = get_random_string()
        self.client.post('/api/token/registration/', {'uid': uid})

        mock_logger_debug.assert_any_call(
            'OLGA registered edX installation with token %s for uid %s',
            mock_uuid4.return_value.access_token,
            uid
        )

        uid = get_random_string()
        self.client.post('/api/token/registration/', {'uid': uid})

        mock_logger_debug.assert_any_call(
            'OLGA registered edX installation with token %s for uid %s',
            mock_uuid4.return_value.access_token,
            uid
        )


@patch('olga.analytics.views.AccessTokenForm.is_valid')
class TestAccessTokenAuthorization(TestCase):
    """
    Tests for access token authorization.
    """

    @patch('olga.analytics.views.AccessTokenAuthorization.is_token_authorized')
    def test_post_method(
            self, mock_is_token_authorized, mock_access_token_form_is_valid
    ):
        """
        Test post method response if request data is valid and edx installation is authorized.
        """
        mock_access_token_form_is_valid.return_value = True
        mock_is_token_authorized.return_value = True

        access_token = uuid.uuid4().hex

        response = self.client.post('/api/token/authorization/', {'access_token': access_token})

        self.assertEqual(httplib.OK, response.status_code)
        self.assertEqual(HttpResponse, response.__class__)

    @patch('olga.analytics.views.uuid4')
    @patch('olga.analytics.views.EdxInstallation.objects.get')
    def test_post_method_if_instance_is_not_authorized(
            self, mock_edx_installation_objects_get, mock_uuid4, mock_access_token_form_is_valid
    ):
        """
        Test post method response if request data is valid and edx installation is not authorized.
        """
        mock_access_token_form_is_valid.return_value = True
        mock_edx_installation_objects_get.side_effect = EdxInstallation.DoesNotExist()
        mock_uuid4.return_value = MockUUID4()

        access_token = uuid.uuid4().hex

        response = self.client.post('/api/token/authorization/', {'access_token': access_token})

        self.assertEqual(httplib.UNAUTHORIZED, response.status_code)
        self.assertEqual(HttpResponse, response.__class__)

    def test_post_method_if_request_data_is_not_valid(self, mock_access_token_form_is_valid):
        """
        Test post method response if request data is not valid.
        """
        mock_access_token_form_is_valid.return_value = False

        access_token = uuid.uuid4().hex

        response = self.client.post('/api/token/authorization/', {'access_token': access_token})

        self.assertEqual(httplib.UNAUTHORIZED, response.status_code)
        self.assertEqual(HttpResponse, response.__class__)


class TestReceiveInstallationStatisticsHelpers(TestCase):
    """
    Tests for receive installation statistics method helpers.
    """

    def setUp(self):
        """
        Create installation default data.
        """
        self.received_data, self.installation_statistics, self.enthusiast_edx_installation = \
            InstallationDefaultData().create_installation_default_data()

        self.access_token = self.received_data.get('access_token')

    def test_update_students_with_no_country(self):
        """
        Verify that update_students_with_no_country method correctly update students without country amount.
        """
        active_students_amount = 40
        students_per_country_before_update = {
            'RU': 10,
            'CA': 5,
            'UA': 20
        }

        result = ReceiveInstallationStatistics.update_students_with_no_country(
            active_students_amount, students_per_country_before_update
        )

        students_per_country_before_update.update({'null': 5})
        expected_students_per_country_after_update = students_per_country_before_update

        self.assertEqual(expected_students_per_country_after_update, result)

    def test_get_students_per_country(self):
        """
        Test get_students_per_country method correctly return students per country value.
        """
        active_students_amount_day = 40
        students_per_country = "{\"RU\": 10, \"CA\": 5, \"UA\": 20}"

        result = ReceiveInstallationStatistics().get_students_per_country(
            students_per_country, active_students_amount_day
        )

        expected_students_per_country = {'RU': 10, 'CA': 5, 'UA': 20, 'null': 5}

        self.assertDictContainsSubset(expected_students_per_country, result)

    def test_extend_stats_if_needed(self):
        """
        Verify that extend_stats_to_enthusiast method extends edx installation fields.
        """
        edx_installation_object = EdxInstallationFactory(
            platform_name=None, platform_url=None, latitude=None, longitude=None
        )

        ReceiveInstallationStatistics().extend_stats_to_enthusiast(
            self.received_data, self.installation_statistics, edx_installation_object
        )

        extended_edx_installation_object_attributes = EdxInstallation.objects.first().__dict__

        self.assertDictContainsSubset(self.enthusiast_edx_installation, extended_edx_installation_object_attributes)

    @patch('olga.analytics.views.ReceiveInstallationStatistics.extend_stats_to_enthusiast')
    @patch('olga.analytics.models.EdxInstallation.objects.get')
    def test_extend_stats_occurs(
            self, mock_edx_installation_objects_get, mock_receive_installation_statistics_extend_stats_to_enthusiast,
    ):
        """
        Verify that extend_stats_to_enthusiast method occurs if edx installation statistics level is enthusiast.
        """
        edx_installation_object = EdxInstallationFactory()

        mock_edx_installation_objects_get.return_value = edx_installation_object

        ReceiveInstallationStatistics().create_instance_data(self.received_data, self.access_token)

        mock_receive_installation_statistics_extend_stats_to_enthusiast.assert_called_once_with(
            self.received_data, self.installation_statistics, edx_installation_object
        )

    @patch('olga.analytics.views.ReceiveInstallationStatistics.extend_stats_to_enthusiast')
    @patch('olga.analytics.models.EdxInstallation.objects.get')
    def test_extend_stats_does_not_occur(
            self, mock_edx_installation_objects_get, mock_receive_installation_statistics_extend_stats_to_enthusiast,
    ):
        """
        Verify that extend_stats_to_enthusiast method does not occurs if edx installation statistics level is paranoid.
        """
        self.received_data['statistics_level'] = 'paranoid'

        edx_installation_object = EdxInstallationFactory()

        mock_edx_installation_objects_get.return_value = edx_installation_object

        ReceiveInstallationStatistics().create_instance_data(self.received_data, self.access_token)

        self.assertEqual(0, mock_receive_installation_statistics_extend_stats_to_enthusiast.call_count)

    @patch('olga.analytics.models.InstallationStatistics.objects.create')
    @patch('olga.analytics.models.EdxInstallation.objects.get')
    def test_installation_stats_creation_occurs(
            self,
            mock_edx_installation_objects_get,
            mock_installation_statistics_installation_objects_create
    ):
        """
        Verify that installation statistic creation was successfully called via `objects.create` method.
        """
        edx_installation_object = EdxInstallationFactory()

        mock_edx_installation_objects_get.return_value = edx_installation_object

        ReceiveInstallationStatistics().create_instance_data(self.received_data, self.access_token)

        # Assertion `mock_installation_statistics_installation_objects_create.assert_called_once_with()` does not work.
        # I did debug, all passed arguments as `edx_installation_object` and `installation_statistics` equal
        # the same parameters in `create_instance_data` method. But tests did not passed.
        mock_installation_statistics_installation_objects_create.assert_called_once()

    @patch('olga.analytics.views.logging.Logger.debug')
    @patch('olga.analytics.models.EdxInstallation.objects.get')
    def test_logger_debug_occurs_if_stats_was_created(
            self,
            mock_edx_installation_objects_get,
            mock_logger_debug
    ):
        """
        Test logger`s debug output occurs if installation was created.
        """
        edx_installation_object = EdxInstallationFactory()

        mock_edx_installation_objects_get.return_value = edx_installation_object

        ReceiveInstallationStatistics().create_instance_data(self.received_data, self.access_token)

        mock_logger_debug.assert_called_once_with('Corresponding data was %s in OLGA database.', 'created')

    @patch('olga.analytics.views.logging.Logger.debug')
    @patch('olga.analytics.models.EdxInstallation.objects.get')
    def test_logger_debug_occurs_if_stats_was_updated(
            self,
            mock_edx_installation_objects_get,
            mock_logger_debug
    ):
        """
        Test logger`s debug output occurs if installation was updated.
        """
        edx_installation_object = EdxInstallationFactory()

        mock_edx_installation_objects_get.return_value = edx_installation_object

        ReceiveInstallationStatistics().create_instance_data(self.received_data, self.access_token)

        ReceiveInstallationStatistics().create_instance_data(self.received_data, self.access_token)

        mock_logger_debug.assert_any_call('Corresponding data was %s in OLGA database.', 'updated')

    @patch('olga.analytics.models.EdxInstallation.objects.filter')
    def test_is_token_authorized_if_instance_is_authorized(self, mock_edx_installation_objects_filter):
        """
        Verify that is_token_authorized method return True if token is authorized.
        """
        mock_edx_installation_objects_filter.return_value = True

        result = AccessTokenAuthorization().is_token_authorized(self.access_token)

        self.assertTrue(result)

    @patch('olga.analytics.views.logging.Logger.debug')
    @patch('olga.analytics.models.EdxInstallation.objects.filter')
    def test_logger_debug_occurs_if_instance_is_authorized(
            self, mock_edx_installation_objects_filter, mock_logger_debug
    ):
        """
        Test logger`s debug output occurs if installation is authorized.
        """
        mock_edx_installation_objects_filter.return_value = True

        AccessTokenAuthorization().is_token_authorized(self.access_token)

        mock_logger_debug.assert_called_once_with(
            'edX installation with token %s was successfully authorized', self.access_token
        )

    @patch('olga.analytics.models.EdxInstallation.objects.get')
    def test_is_token_authorized_if_is_not_authorized(self, mock_edx_installation_objects_get):
        """
        Verify that is_token_authorized method return False if token is not authorized.
        """
        mock_edx_installation_objects_get.side_effect = EdxInstallation.DoesNotExist()

        result = AccessTokenAuthorization().is_token_authorized(self.access_token)

        self.assertFalse(result)

    @patch('olga.analytics.views.logging.Logger.debug')
    @patch('olga.analytics.models.EdxInstallation.objects.get')
    def test_logger_debug_occurs_if_instance_is_unauthorized(
            self, mock_edx_installation_objects_get, mock_logger_debug
    ):
        """
        Test logger`s debug output occurs if installation is not authorized.
        """
        mock_edx_installation_objects_get.side_effect = EdxInstallation.DoesNotExist()

        AccessTokenAuthorization().is_token_authorized(self.access_token)

        mock_logger_debug.assert_called_once_with(
            'edX installation with token %s was not authorized', self.access_token
        )

    @patch('olga.analytics.views.logging.Logger.debug')
    def test_log_debug_instance_details(self, mock_logger_debug):
        """
        Test logger`s debug output occurs installation details.
        """
        ReceiveInstallationStatistics().log_debug_instance_details(self.received_data)

        expected_logger_debugs = [
            call((
                json.dumps(self.received_data, sort_keys=True, indent=4)
            ), ),
        ]

        self.assertEqual(expected_logger_debugs, mock_logger_debug.call_args_list)


class TestReceiveInstallationStatistics(TestCase):
    """
    Tests for receive installation statistics.
    """

    def setUp(self):
        """
        Create installation default data.
        """
        self.received_data, _, __ = InstallationDefaultData().create_installation_default_data()
        self.access_token = self.received_data.get('access_token')
        self.received_data_as_query_dict = self.create_query_dict_from_dict(self.received_data)

        EdxInstallationFactory(access_token=self.access_token)

    @staticmethod
    def create_query_dict_from_dict(simple_dict):
        """
        Convert common dictionary to query dictionary, that uses in request processes.
        """
        simple_dict_deep_copy = copy.deepcopy(simple_dict)

        query_dict = QueryDict('', mutable=True)
        query_dict.update(simple_dict_deep_copy)

        return query_dict

    def test_post_method(self):
        """
        Test post method response if edx installation was authorized and data was created.
        """
        response = self.client.post('/api/installation/statistics/', self.received_data)

        self.assertEqual(httplib.CREATED, response.status_code)
        self.assertEqual(HttpResponse, response.__class__)

    @patch('olga.analytics.views.AccessTokenAuthorization.is_token_authorized')
    def test_post_method_if_token_is_unauthorized(self, mock_is_token_authorized):
        """
        Test post method response if edx installation was unauthorized.
        """
        mock_is_token_authorized.return_value = False

        response = self.client.post('/api/installation/statistics/', self.received_data)

        self.assertEqual(httplib.UNAUTHORIZED, response.status_code)
        self.assertEqual(HttpResponse, response.__class__)

    @patch('olga.analytics.views.AccessTokenAuthorization.is_token_authorized')
    def test_is_token_authorized_occurs(self, mock_is_token_authorized):
        """
        Verify occurring is_token_authorized method.
        """
        self.client.post('/api/installation/statistics/', self.received_data)
        mock_is_token_authorized.assert_called_once_with(self.access_token)

    @patch('olga.analytics.views.ReceiveInstallationStatistics.log_debug_instance_details')
    def test_log_debug_instance_details(self, mock_logger_debug_instance_details):
        """
        Verify that logger`s debug output occurs.
        """
        self.client.post('/api/installation/statistics/', self.received_data)
        mock_logger_debug_instance_details.assert_called_once_with(self.received_data_as_query_dict)

    @patch('olga.analytics.views.ReceiveInstallationStatistics.create_instance_data')
    def test_create_instance_data_occurs(self, mock_create_instance_data):
        """
        Verify that create_instance_data method occurs during post method`s process.
        """
        self.client.post('/api/installation/statistics/', self.received_data)
        mock_create_instance_data.assert_called_once_with(self.received_data_as_query_dict, self.access_token)

    def test_multiply_create_instance_data_in_same_day(self):
        """
        Verify that when double calls are sent statistic from one instance only one record will be created.
        """
        self.client.post('/api/installation/statistics/', self.received_data)
        self.assertEqual(1, InstallationStatistics.objects.all().count())

        self.received_data['active_students_amount_day'] *= 2
        self.client.post('/api/installation/statistics/', self.received_data)
        stats = InstallationStatistics.objects.all()
        self.assertEqual(1, stats.count())
        self.assertEqual(
            int(self.received_data['active_students_amount_day']),
            stats[0].active_students_amount_day
        )

    def test_multiply_create_instance_data_in_different_day(self):
        """
        Verify that when double calls are sent statistic in different days there are two records will be created.
        """
        self.client.post('/api/installation/statistics/', self.received_data)
        stats = InstallationStatistics.objects.all()
        self.assertEqual(1, stats.count())
        stats.update(data_created_datetime=(datetime.now() - timedelta(days=1)))

        self.client.post('/api/installation/statistics/', self.received_data)
        self.assertEqual(2, InstallationStatistics.objects.all().count())
