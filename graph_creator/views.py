import uuid
import json

import requests

from django.conf import settings
from django.core import serializers
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View
from django.utils.decorators import method_decorator

from .models import DataStorage


class IndexView(View):
    """
    Displays information on a world map.

    Retrieve information about edx-platform from DB, serialize it into JSON format and
    pass serialized data to the template. The template displays a map of the world with the
    edx-platform marker on it.

    `edx_data_as_json` is a `DataStorage` containing all information about edx-platform.

    Returns http response and passes `edx_data_as_json` data as a context variable `edx_data`
    to the `index.html` template.
    """

    def get(self, request, *args, **kwargs):
        """
        Retrieve information about edx-platform from DB and serialize it into JSON.

        `edx_data_as_json` is a `DataStorage` containing all information about edx-platform.
        """

        edx_data_as_json = serializers.serialize('json', DataStorage.objects.all())
        return render(request, 'graph_creator/index.html', {'edx_data': edx_data_as_json})


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
    def students_per_country(active_students_amount, students_per_country):
        """
        Method calculates amount of students per country.

        Arguments:
            active_students_amount (int): Count of active students.
            students_per_country (list): List of dictionaries, where one of them is country-count accordance.
                                         Amount of students without country is empty.

        Returns:
            students_per_country (list): List of dictionaries, where one of them is country-count accordance.
                                         Amount of students without country has calculated.
        """

        students_per_country[0]['count'] = active_students_amount - sum(
            [country['count'] for country in students_per_country]
        )

        return students_per_country

    def create_instance_data(self, received_data, secret_token):
        """
        Method provides saving instance data as object in database.

        Arguments:
            received_data (QueryDict): Request data from edX instance.
            secret_token (unicode): Secret key to allow edX instance send a data to server.
                                    If token is empty, it will be generated with uuid.UUID in string format.
        """

        active_students_amount = int(received_data.get('active_students_amount'))
        courses_amount = int(received_data.get('courses_amount'))
        statistics_level = received_data.get('statistics_level')

        instance_data = {
            'active_students_amount': active_students_amount,
            'courses_amount': courses_amount,
            'secret_token': secret_token,
            'statistics_level': statistics_level
        }

        if statistics_level == 'enthusiast':

            # Decoded to process and encoded to save in database list of dictionaries,
            # that contains amount of students per country
            students_per_country = json.loads(received_data.get('students_per_country'))
            students_per_country = json.dumps(self.students_per_country(
                    active_students_amount, students_per_country
            ))

            enthusiast_data = {
                'latitude': float(received_data.get('latitude')),
                'longitude': float(received_data.get('longitude')),
                'platform_name': received_data.get('platform_name'),
                'platform_url': received_data.get('platform_url'),
                'students_per_country': students_per_country
            }

            instance_data.update(enthusiast_data)

        DataStorage.objects.create(**instance_data)

    def post(self, request, *args, **kwargs):
        """
        Receive information from the edx-platform and processes it.

        If the first time gets information from edx-platform, generates a secret token and
        sends it back to the edx-platform for further data exchange abilities, otherwise
        updates data in the DB with the new incoming information from the edx-platform.

        Returns HTTP-response with status 201, that means object (instance data) was successfully created.
        """

        received_data = self.request.POST
        platform_url = received_data.get('platform_url')
        secret_token = received_data.get('secret_token')

        if secret_token:
            self.create_instance_data(received_data, secret_token)

        else:
            secret_token = uuid.uuid4().hex
            self.create_instance_data(received_data, secret_token)

            if settings.DEBUG:
                edx_url = settings.EDX_PLATFORM_POST_URL_LOCAL
            else:
                edx_url = platform_url + '/acceptor_data/'

            requests.post(
                edx_url, data={'secret_token': secret_token}
            )

        return HttpResponse(status=201)
