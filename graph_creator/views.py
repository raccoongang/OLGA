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
    def students_per_country(active_students_amount, students_per_country_to_decode):
        """
        Method calculates amount of students per country.

        Arguments:
            active_students_amount (int): Count of activate students.
            students_per_country_to_decode (unicode): Unicode oriented to decode in list of dictionaries.

        Returns:
            students_per_country (str) : List of dictionaries, where one of them is country-count accordance.
        """

        students_per_country = json.loads(students_per_country_to_decode)

        students_per_country[0]['count'] = active_students_amount - sum(
            [country['count'] for country in students_per_country]
        )

        students_per_country = json.dumps(students_per_country)

        return students_per_country

    def post(self, request, *args, **kwargs):
        """
        Receive information from the edx-platform and processes it.

        If the first time gets information from edx-platform, generates a secret token and
        sends it back to the edx-platform for further data exchange abilities, otherwise
        updates data in the DB with the new incoming information from the edx-platform.

        `secret_token` when generates is a uuid.UUID in string format.
        `reverse_token` is a requests. Sends the secret token to edx-platform.

        Returns http response redirecting to the main page.
        """

        received_data = self.request.POST
        level = received_data.get('level')
        secret_token = received_data.get('secret_token')
        active_students_amount = int(received_data.get('active_students_amount'))

        if secret_token:
            if level == 'enthusiast':

                instance_data = {
                    'active_students_amount': active_students_amount,
                    'courses_amount': int(received_data.get('courses_amount')),
                    'latitude': float(received_data.get('latitude')),
                    'level': level,
                    'longitude': float(received_data.get('longitude')),
                    'platform_name': received_data.get('platform_name'),
                    'platform_url': received_data.get('platform_url'),
                    'secret_token': secret_token,
                    'students_per_country': self.students_per_country(
                        active_students_amount, received_data.get('students_per_country')
                    )
                }

            else:  # level is paranoid
                instance_data = {
                    'active_students_amount': active_students_amount,
                    'courses_amount': int(received_data.get('courses_amount')),
                    'level': level,
                    'secret_token': secret_token
                }

            DataStorage.objects.create(**instance_data)
            return HttpResponse(status=200)

        else:
            secret_token = uuid.uuid4().hex

            instance_data = {
                'active_students_amount': active_students_amount,
                'courses_amount': int(received_data.get('courses_amount')),
                'latitude': float(received_data.get('latitude')),
                'level': level,
                'longitude': float(received_data.get('longitude')),
                'platform_name': received_data.get('platform_name'),
                'platform_url': received_data.get('platform_url'),
                'secret_token': secret_token,
                'students_per_country': self.students_per_country(
                        active_students_amount, received_data.get('students_per_country')
                )
            }

            if settings.DEBUG:
                requests.post(
                    # Local IP address of the edx-platform running within VM.
                    settings.EDX_PLATFORM_POST_URL_LOCAL, data={"secret_token": secret_token}
                )
                return HttpResponse(status=201)

            else:
                requests.post(
                    str(instance_data['platform_url']) + '/acceptor_data/', data={"secret_token": secret_token}
                )
                return HttpResponse(status=201)
