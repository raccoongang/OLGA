from django.shortcuts import render
from django.views.generic import View
import uuid
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.conf import settings
from django.http import HttpResponse
import requests

from .models import DataStorage

HTTP_201_CREATED = 201
@method_decorator(csrf_exempt, name='dispatch')
class ReceiveData(View):
    """
    Receives and processes data from the remote edx-platform.

    If the platform has already registered, a normal data exchange happens.
    Otherwise generates a secret token, (registers)saves it to DB with the edx-platform's incoming URL
    and sends newly generated token to the edx-platform for further
    data interchange abilities with the server.
    """

    @staticmethod
    def update_students_without_no_country_value(active_students_amount, students_per_country):
        # pylint: disable=invalid-name
        """
        Method calculates amount of students, that have no country and update overall variable (example below).

        Problem is a query (sql, group by `country`) does not count students without country.
        To know how many students have no country, we need subtract summarize amount of students with country from
        all active students we got with edX`s received data (post-request).

        Arguments:
            active_students_amount (int): Count of active students.
            students_per_country (dictionary): Country-count accordance as pair of key-value.
                                               Amount of students without country is empty (key 'null' with value 0)

        Returns:
            students_per_country (dictionary): Country-count accordance as pair of key-value.
                                         Amount of students without country has calculated and inserted to
                                         corresponding key ('null').
        """

        students_per_country['null'] = active_students_amount - sum(students_per_country.values())

        return students_per_country

    def create_instance_data(self, received_data, secret_token):
        """
        Method provides saving instance data as object in database.

        Arguments:
            received_data (QueryDict): Request data from edX instance.
            secret_token (unicode): Secret key to allow edX instance send a data to server.
                                    If token is empty, it will be generated with uuid.UUID in string format.
        """

        active_students_amount_day = int(received_data.get('active_students_amount_day'))
        active_students_amount_week = int(received_data.get('active_students_amount_week'))
        active_students_amount_month = int(received_data.get('active_students_amount_month'))
        courses_amount = int(received_data.get('courses_amount'))
        statistics_level = received_data.get('statistics_level')

        instance_data = {
            'active_students_amount_day': active_students_amount_day,
            'active_students_amount_week': active_students_amount_week,
            'active_students_amount_month': active_students_amount_month,
            'courses_amount': courses_amount,
            'secret_token': secret_token,
            'statistics_level': statistics_level
        }

        if statistics_level == 'enthusiast':

            # Decoded to process and encoded to save in database list of dictionaries,
            # that contains amount of students per country
            students_per_country_decoded = json.loads(received_data.get('students_per_country'))
            students_per_country_encoded = json.dumps(self.update_students_without_no_country_value(
                active_students_amount_month, students_per_country_decoded
            ))

            enthusiast_data = {
                'latitude': float(received_data.get('latitude')),
                'longitude': float(received_data.get('longitude')),
                'platform_name': received_data.get('platform_name'),
                'platform_url': received_data.get('platform_url'),
                'students_per_country': students_per_country_encoded
            }

            instance_data.update(enthusiast_data)

        DataStorage.objects.create(**instance_data)

    def post(self, request):
        """
        Receives information from the edx-platform and processes it.

        If the first time gets information from edx-platform, generates a secret token and
        sends it back to the edx-platform for further data exchange abilities, otherwise
        updates data in the DB with the new incoming information from the edx-platform.

        Returns HTTP-response with status 201, that means object (instance data) was successfully created.
        """

        received_data = self.request.POST
        platform_url = received_data.get('platform_url')
        secret_token = received_data.get('secret_token')

        if not secret_token:
            secret_token = uuid.uuid4().hex
            edx_url = settings.EDX_PLATFORM_POST_URL_LOCAL if settings.DEBUG else (platform_url + '/acceptor_data/')
            requests.post(edx_url, data={'secret_token': secret_token})

        self.create_instance_data(received_data, secret_token)
        return HttpResponse(status=HTTP_201_CREATED)
