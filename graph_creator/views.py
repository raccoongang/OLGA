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
from django.db.models import Sum

from .models import DataStorage


HTTP_201_CREATED = 201


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


class GraphsView(View):
    """
    Provide data and plot 3 main graphs:

    1. Number of students per date
    2. Number of courses per date
    3. Number of instances per date
    """   

    def get(self, request, *args, **kwargs):
        """
        Pass graph data to frontend.
        """
        timeline = DataStorage.timeline()
        students, courses, instances = DataStorage.data_per_period()
        instances_count, courses_count, students_count = DataStorage.overall_counts()

        context = {
            'timeline': json.dumps(timeline),
            'students': json.dumps(students),
            'courses': json.dumps(courses),
            'instances': json.dumps(instances),
            'instances_count': instances_count,
            'courses_count': courses_count,
            'students_count': students_count
        }

        return render(request, 'graph_creator/graphs.html', context)


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
        """
        Method calculates amount of students, that have no country and update overall variable (example below).

        `students_per_country` has next form: '[{u'count': 0, u'country': None}, {u'count': 1, u'country': u'UA'},
                                               {u'count': 1, u'country': u'RU'}, ...]'

        Problem is a query (sql, group by `country`) does not count students without country.
        To know how many students have no country, we need subtract summarize amount of students with country from
        all active students we got with edX`s received data (post-request).

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
            students_per_country_decoded = json.loads(received_data.get('students_per_country'))
            students_per_country_encoded = json.dumps(self.update_students_without_no_country_value(
                    active_students_amount, students_per_country_decoded
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

        if not secret_token:
            secret_token = uuid.uuid4().hex
            edx_url = settings.EDX_PLATFORM_POST_URL_LOCAL if settings.DEBUG else (platform_url + '/acceptor_data/')
            requests.post(edx_url, data={'secret_token': secret_token})

        self.create_instance_data(received_data, secret_token)
        return HttpResponse(status=HTTP_201_CREATED)
