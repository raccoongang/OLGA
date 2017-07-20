"""
Views for the analytics application.
"""

import copy
import httplib
import json
import logging
from uuid import uuid4

from django.http import HttpResponse
from django.http import JsonResponse
from django.views.generic import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from .forms import AccessTokenForm
from .models import EdxInstallation, InstallationStatistics
from .utils import validate_instance_stats_forms

logging.basicConfig()

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


@method_decorator(csrf_exempt, name='dispatch')
class AccessTokenRegistration(View):
    """
    Provide access token registration functionality.
    """

    @staticmethod
    def create_edx_installation(access_token):
        """
        Create edx installation: insert access token field.

        Access token is enough to fetching, sending and dispatching statistics. It called `Paranoid` level.
        """
        EdxInstallation.objects.create(access_token=access_token)

    def post(self, request):  # pylint: disable=unused-argument
        """
        Receive primary edX installation request for getting access for dispatch statistics via token.

        Returns HTTP-response with status 201, that means object (installation token) was successfully created.
        """
        access_token = uuid4().hex
        self.create_edx_installation(access_token)

        logger.debug('OLGA acceptor registered edX installation with token %s', access_token)
        return JsonResponse({'access_token': access_token}, status=httplib.CREATED)


@method_decorator(csrf_exempt, name='dispatch')
class AccessTokenAuthorization(View):
    """
    Provide access token authorization functionality.
    """

    @staticmethod
    def post(request):
        """
        Verify that installation is allowed access to dispatch installation statistics.

        Returns HTTP-response with status 200, that means object (installation) with received token exists.
        Returns HTTP-response with status 401 and refreshed access token, that means object (installation) with
        received token does not exist and edX installation need to get new one,
        """
        access_token_serializer = AccessTokenForm(request.POST)

        if access_token_serializer.is_valid():
            access_token = str(request.POST.get('access_token'))

            try:
                EdxInstallation.objects.get(access_token=access_token)

                logger.debug('edX installation with token %s was successfully authorized', access_token)
                return HttpResponse(status=httplib.OK)

            except EdxInstallation.DoesNotExist:
                logger.debug(
                    'edX installation has no corresponding data in OLGA acceptor database (no received token). '
                    'Received token is %s.', access_token
                )

                refreshed_access_token = uuid4().hex
                AccessTokenRegistration().create_edx_installation(refreshed_access_token)

                logger.debug('Refreshed token for edX installation is %s', refreshed_access_token)
                return JsonResponse({'refreshed_access_token': refreshed_access_token}, status=httplib.UNAUTHORIZED)

        return HttpResponse(status=httplib.UNAUTHORIZED)


@method_decorator(csrf_exempt, name='dispatch')
class ReceiveInstallationStatistics(View):
    """
    Provide edX installation statistics reception and processing functionality.
    """

    @staticmethod
    def update_students_with_no_country(active_students_amount, students_per_country_before_update):
        # pylint: disable=invalid-name
        """
        Calculate amount of students, that have no country and update overall variable (example below).

        Problem is a query (sql, group by `country`) does not count students without country.
        To know how many students have no country, we need subtract summarize amount of students with country from
        all active students we got with edX's received data (post-request).

        Arguments:
            active_students_amount (int): Active students amount.
            students_per_country_before_update (dict): Country-count accordance as pair of key-value.
                                                       Amount of students without country may be particular value or
                                                       may be empty (key 'null' with value 0).

        Returns:
            students_per_country_after_update (dict): Country-count accordance as pair of key-value.
                                                      Amount of students without country has calculated
                                                      and inserted to corresponding key ('null').

        """
        students_per_country_after_update = copy.deepcopy(students_per_country_before_update)
        # pylint: disable=invalid-name

        students_per_country_after_update['null'] = \
            active_students_amount - sum(students_per_country_after_update.values())

        return students_per_country_after_update

    def get_students_per_country(self, students_per_country, active_students_amount_day):
        """
        Get students per country in json-based encoded string for saving to database.

        Method's flow:
        1. Load json-based students per country string and save to `students_per_country_decoded` variable.
        2. Calculate students without country value via `update_students_with_no_country` method.
        3. Dumps students per country dictionary to json-based string for storing in database.
        """
        students_per_country_decoded = json.loads(students_per_country)

        students_per_country_updated = self.update_students_with_no_country(
            active_students_amount_day, students_per_country_decoded
        )

        students_per_country_encoded = json.dumps(students_per_country_updated)

        return students_per_country_encoded

    def extend_stats_to_enthusiast(self, received_data, installation_statistics, edx_installation_object):
        """
        Extend installation statistics level from `Paranoid` to `Enthusiast`.

        It contains additional information about installation:
            - latitude, longitude;
            - platform name, platform url;
            - students per country.
        """
        students_per_country = self.get_students_per_country(
            received_data.get('students_per_country'), int(received_data.get('active_students_amount_day'))
        )

        enthusiast_edx_installation = {
            'latitude': float(received_data.get('latitude')),
            'longitude': float(received_data.get('longitude')),
            'platform_name': received_data.get('platform_name'),
            'platform_url': received_data.get('platform_url'),
        }

        enthusiast_statistics = {
            'students_per_country': students_per_country
        }

        installation_statistics.update(enthusiast_statistics)

        if edx_installation_object.does_edx_installation_extend_level_first_time():
            edx_installation_object.update_edx_instance_info(enthusiast_edx_installation)

    def create_instance_data(self, received_data, access_token):
        """
        Save edX installation data into a database.

        Arguments:
            received_data (QueryDict): Request data from edX instance.
            access_token (unicode): Secret key to allow edX instance send a data to server.
                                    If token is empty, it will be generated with uuid.UUID in string format.
        """
        active_students_amount_day = int(received_data.get('active_students_amount_day'))
        active_students_amount_week = int(received_data.get('active_students_amount_week'))
        active_students_amount_month = int(received_data.get('active_students_amount_month'))
        courses_amount = int(received_data.get('courses_amount'))
        statistics_level = received_data.get('statistics_level')

        installation_statistics = {
            'active_students_amount_day': active_students_amount_day,
            'active_students_amount_week': active_students_amount_week,
            'active_students_amount_month': active_students_amount_month,
            'courses_amount': courses_amount,
            'statistics_level': statistics_level
        }

        edx_installation_object = EdxInstallation.objects.get(access_token=access_token)

        if statistics_level == 'enthusiast':
            self.extend_stats_to_enthusiast(received_data, installation_statistics, edx_installation_object)

        InstallationStatistics.objects.create(edx_installation=edx_installation_object, **installation_statistics)
        logger.debug('Corresponding data was created in OLGA acceptor database.')

    @staticmethod
    def is_access_token_authorized(access_token):
        """
        Check if access token belongs to any EdxInstallation object.
        """
        try:
            EdxInstallation.objects.get(access_token=access_token)
            logger.debug('edX installation with token %s was successfully authorized', access_token)
            return True
        except EdxInstallation.DoesNotExist:
            logger.debug('edX installation with token %s was not authorized', access_token)
            return False

    @staticmethod
    def logger_debug_instance_details(received_data):
        """
        Log edx installation information and statistics.
        """
        logger.debug(
            'edX installation called %s from %s sent statistics after authorization',
            received_data.get('platform_name'),
            received_data.get('platform_url')
        )

        logger.debug(json.dumps(received_data, sort_keys=True, indent=4))

    @method_decorator(validate_instance_stats_forms)
    def post(self, request):
        """
        Receive edX installation statistics and create corresponding data in database.

        Returns HTTP-response with status 201, that means object (installation data) was successfully created.
        Returns HTTP-response with status 401, that means edX installation is not authorized via token.
        """
        received_data = request.POST
        access_token = received_data.get('access_token')

        if self.is_access_token_authorized(access_token):
            self.logger_debug_instance_details(received_data)

            self.create_instance_data(received_data, access_token)
            return HttpResponse(status=httplib.CREATED)

        return HttpResponse(status=httplib.UNAUTHORIZED)
