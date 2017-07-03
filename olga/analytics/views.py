"""
Views for the analytics application.
"""

import json
import uuid

from django.http import HttpResponse
from django.views.generic import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from .forms import AccessTokenForm
from .models import InstallationStatistics, EdxInstallation
from .utils import installation_statistics_forms_checker

HTTP_200_OK = 200
HTTP_201_CREATED = 201
HTTP_401_UNAUTHORIZED = 401


@method_decorator(csrf_exempt, name='dispatch')
class AccessTokenRegistration(View):
    """
    Provides access token registration functionality.
    """

    @staticmethod
    def registry_a_token_and_return_it():
        """
        Create UUID based access token ans store it in database.

        Returns same access token.
        """

        access_token = uuid.uuid4().hex
        EdxInstallation.objects.create(access_token=access_token)

        return access_token

    def post(self, request):  # pylint: disable=unused-argument
        """
        Receives primary edX installation request for getting access for dispatch statistics via token.

        Returns HTTP-response with status 201, that means object (installation token) was successfully created.
        """

        token_registration_response = json.dumps({
            'access_token': self.registry_a_token_and_return_it()
        })

        return HttpResponse(token_registration_response, status=HTTP_201_CREATED)


@method_decorator(csrf_exempt, name='dispatch')
class AccessTokenAuthorization(View):
    """
    Provides access token authorization functionality.
    """

    @staticmethod
    def post(request):
        """
        Verifies that installation is allowed access to dispatch installation statistics.

        Returns HTTP-response with status 200, that means object (installation) with received token exists.
        Returns HTTP-response with status 401 and refreshed access token, that means object (installation) with
        received token does not exist and edX installation need to get new one,
        """

        access_token_serializer = AccessTokenForm(request.POST)

        if access_token_serializer.is_valid():
            access_token = request.POST.get('access_token')

            try:
                EdxInstallation.objects.get(access_token=access_token)
                return HttpResponse(status=HTTP_200_OK)

            except EdxInstallation.DoesNotExist:
                token_authorization_response = json.dumps({
                    'refreshed_access_token': AccessTokenRegistration.registry_a_token_and_return_it()
                })

                return HttpResponse(token_authorization_response, status=HTTP_401_UNAUTHORIZED)

        return HttpResponse(status=HTTP_401_UNAUTHORIZED)


@method_decorator(csrf_exempt, name='dispatch')
class ReceiveInstallationStatistics(View):
    """
    Provides edX installation statistics reception and processing functionality.
    """

    @staticmethod
    def update_students_without_country_value(active_students_amount, students_per_country):
        # pylint: disable=invalid-name
        """
        Calculates amount of students, that have no country and update overall variable (example below).

        Problem is a query (sql, group by `country`) does not count students without country.
        To know how many students have no country, we need subtract summarize amount of students with country from
        all active students we got with edX's received data (post-request).

        Arguments:
            active_students_amount (int): Count of active students.
            students_per_country (dict): Country-count accordance as pair of key-value.
                                         Amount of students without country is empty (key 'null' with value 0)

        Returns:
            students_per_country (dict): Country-count accordance as pair of key-value.
                                         Amount of students without country has calculated and inserted to
                                         corresponding key ('null').
        """

        students_per_country['null'] = active_students_amount - sum(students_per_country.values())

        return students_per_country


    def extend_statistics_to_enthusiast_level(self, received_data, installation_statistics, edx_installation_object):
        """
        Extends installation statistics level from `Paranoid` to `Enthusiast`.

        It contains additional information about installation:
            - latitude, longitude;
            - platform name, platform url;
            - students per country.
        """

        active_students_amount_day = int(received_data.get('active_students_amount_day'))

        # Decoded to process and encoded to save in database list of dictionaries,
        # that contains amount of students per country
        students_per_country_decoded = json.loads(received_data.get('students_per_country'))
        students_per_country_encoded = json.dumps(self.update_students_without_country_value(
            active_students_amount_day, students_per_country_decoded
        ))

        enthusiast_edx_installation = {
            'latitude': float(received_data.get('latitude')),
            'longitude': float(received_data.get('longitude')),
            'platform_name': received_data.get('platform_name'),
            'platform_url': received_data.get('platform_url'),
        }

        enthusiast_installation_statistics = {  # pylint: disable=invalid-name
            'students_per_country': students_per_country_encoded
        }

        installation_statistics.update(enthusiast_installation_statistics)

        if not edx_installation_object.platform_url:
            edx_installation_object.latitude = enthusiast_edx_installation['latitude']
            edx_installation_object.longitude = enthusiast_edx_installation['longitude']
            edx_installation_object.platform_name = enthusiast_edx_installation['platform_name']
            edx_installation_object.platform_url = enthusiast_edx_installation['platform_url']
            edx_installation_object.save()

    def create_instance_data(self, received_data, access_token):  # pylint: disable=too-many-locals
        """
        Provides saving edX installation data in database.

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
            self.extend_statistics_to_enthusiast_level(received_data, installation_statistics, edx_installation_object)

        InstallationStatistics.objects.create(edx_installation=edx_installation_object, **installation_statistics)

    @staticmethod
    def is_access_token_authorized(access_token):
        """
        Check if access token belongs to any EdxInstallation object.
        """

        try:
            EdxInstallation.objects.get(access_token=access_token)
            return True
        except EdxInstallation.DoesNotExist:
            return False

    @method_decorator(installation_statistics_forms_checker)
    def post(self, request):
        """
        Receives edX installation statistics and create corresponding data in database.

        Returns HTTP-response with status 201, that means object (installation data) was successfully created.
        Returns HTTP-response with status 401, that means edX installation is not authorized via token.
        """

        received_data = request.POST
        access_token = received_data.get('access_token')

        if self.is_access_token_authorized(access_token):
            self.create_instance_data(received_data, access_token)
            return HttpResponse(status=HTTP_201_CREATED)

        return HttpResponse(status=HTTP_401_UNAUTHORIZED)
