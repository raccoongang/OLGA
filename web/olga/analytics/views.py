"""
Views for the analytics application.
"""

import copy
import hashlib
import httplib
import json
import logging
from uuid import uuid4

import datetime
from django.http import HttpResponse
from django.http import JsonResponse
from django.views.generic import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from olga.analytics.forms import AccessTokenForm
from olga.analytics.models import EdxInstallation, InstallationStatistics
from olga.analytics.utils import validate_instance_stats_forms

logging.basicConfig()

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


@method_decorator(csrf_exempt, name='dispatch')
class AccessTokenRegistration(View):
    """
    Provide access token registration functionality.
    """

    @staticmethod
    def create_new_edx_instance(access_token, uid):
        """
        Create new edx instance with given access_token and uid.
        """
        EdxInstallation.objects.create(access_token=access_token, uid=uid)
        logger.debug('OLGA registered edX installation with token %s for uid %s', access_token, uid)

    @staticmethod
    def get_access_token(uid):
        """
        Provide access token for the given uid.

        If uid already exist in database - return access token from storage,
        otherwise return generated uid and flag for it creation
        :param uid: instance uid.
        :return tuple(access_token, new_token)
        """
        installation_data = EdxInstallation.objects.filter(uid=uid)
        if installation_data.exists():
            access_token = installation_data[0].access_token
            logger.debug('OLGA get previous edX installation with token %s for uid %s', access_token, uid)
            new_token = False
        else:
            access_token = uuid4().hex
            new_token = True
        return access_token, new_token

    def post(self, request):  # pylint: disable=unused-argument
        """
        Receive primary edX installation request for getting access for dispatch statistics via token.

        Returns HTTP-response with status 201, that means object (installation token) was successfully created.
        """
        uid = hashlib.md5(request.META['HTTP_X_FORWARDED_FOR']).hexdigest()
        access_token, new_token = self.get_access_token(uid)
        if new_token:
            self.create_new_edx_instance(access_token, uid)
        return JsonResponse({'access_token': access_token}, status=httplib.CREATED)


@method_decorator(csrf_exempt, name='dispatch')
class AccessTokenAuthorization(View):
    """
    Provide access token authorization functionality.
    """

    @staticmethod
    def is_token_authorized(access_token):
        """
        Check if access token belongs to any EdxInstallation object.
        """
        if EdxInstallation.objects.filter(access_token=access_token):
            logger.debug('edX installation with token %s was successfully authorized', access_token)
            return True

        logger.debug('edX installation with token %s was not authorized', access_token)
        return False

    def post(self, request):
        """
        Verify that installation is allowed access to dispatch installation statistics.

        Returns HTTP-response with status 200, that means object (installation) with received token exists.
        Returns HTTP-response with status 401 and refreshed access token, that means object (installation) with
        received token does not exist and edX installation need to get new one,
        """
        access_token_serializer = AccessTokenForm(request.POST)
        access_token = str(request.POST.get('access_token'))

        if access_token_serializer.is_valid():
            if self.is_token_authorized(access_token):
                return HttpResponse(status=httplib.OK)

        return HttpResponse(status=httplib.UNAUTHORIZED)


@method_decorator(csrf_exempt, name='dispatch')
class ReceiveInstallationStatistics(View):
    """
    Provide edX installation statistics reception and processing functionality.
    """

    @staticmethod
    def update_students_with_no_country(active_students_amount, students_before_update):
        """
        Calculate amount of students, that have no country and update overall variable (example below).

        Problem is a query (sql, group by `country`) does not count students without country.
        To know how many students have no country, we need subtract summarize amount of students with country from
        all active students we got with edX's received data (post-request).

        Arguments:
            active_students_amount (int): Active students amount.
            students_before_update (dict): Country-count accordance as pair of key-value.
                                           Amount of students without country may be particular value or
                                           may be empty (key 'null' with value 0).

        Returns:
            students_after_update (dict): Country-count accordance as pair of key-value.
                                          Amount of students without country has calculated
                                          and inserted to corresponding key ('null').
        """
        students_after_update = copy.deepcopy(students_before_update)

        students_after_update['null'] = \
            active_students_amount - sum(students_after_update.values())

        return students_after_update

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

        return students_per_country_updated

    def extend_stats_to_enthusiast(self, received_data, stats, edx_installation_object):
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
            'statistics_level': 'enthusiast',
            'students_per_country': students_per_country
        }

        stats.update(enthusiast_statistics)

        edx_installation_object.latitude = enthusiast_edx_installation['latitude']
        edx_installation_object.longitude = enthusiast_edx_installation['longitude']
        edx_installation_object.platform_name = enthusiast_edx_installation['platform_name']
        edx_installation_object.platform_url = enthusiast_edx_installation['platform_url']
        edx_installation_object.save()

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

        stats = {
            'active_students_amount_day': active_students_amount_day,
            'active_students_amount_week': active_students_amount_week,
            'active_students_amount_month': active_students_amount_month,
            'courses_amount': courses_amount,
            'statistics_level': statistics_level
        }

        edx_installation_object = EdxInstallation.objects.get(access_token=access_token)

        if statistics_level == 'enthusiast':
            self.extend_stats_to_enthusiast(received_data, stats, edx_installation_object)

        previous_stats = InstallationStatistics.get_stats_for_this_day(edx_installation_object)
        log_msg = 'Corresponding data was %s in OLGA database.'
        if previous_stats:
            stats['data_created_datetime'] = datetime.datetime.now()
            previous_stats.update(stats)
            logger.debug(log_msg, 'updated')
        else:
            InstallationStatistics.objects.create(edx_installation=edx_installation_object, **stats)
            logger.debug(log_msg, 'created')

    @staticmethod
    def log_debug_instance_details(received_data):
        """
        Log edx installation information and statistics.
        """
        logger.debug(json.dumps(received_data, sort_keys=True, indent=4))

    def log_client_ip(self, request):
        """
        Log client IP address.
        """
        logger.debug('Statistics was sent from IP: %s', self.get_client_ip(request))

    @staticmethod
    def get_client_ip(request):
        """
        Get client IP address.

        Borrowed solution from `https://stackoverflow.com/a/4581997`.
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            client_ip = x_forwarded_for.split(',')[0]
        else:
            client_ip = request.META.get('REMOTE_ADDR')
        return client_ip

    @method_decorator(validate_instance_stats_forms)
    def post(self, request):
        """
        Receive edX installation statistics and create corresponding data in database.

        Returns HTTP-response with status 201, that means object (installation data) was successfully created.
        Returns HTTP-response with status 401, that means edX installation is not authorized via token.
        """
        received_data = request.POST
        access_token = received_data.get('access_token')

        if AccessTokenAuthorization().is_token_authorized(access_token):
            self.log_debug_instance_details(received_data)
            self.log_client_ip(request)

            self.create_instance_data(received_data, access_token)
            return HttpResponse(status=httplib.CREATED)

        return HttpResponse(status=httplib.UNAUTHORIZED)
