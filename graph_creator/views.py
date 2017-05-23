"""
Views for the graph_creator application.
"""

from __future__ import division
import uuid
import json

import requests
import pycountry

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View
from django.utils.decorators import method_decorator

from .models import DataStorage

HTTP_201_CREATED = 201


class MapView(View):
    """
    Displays information on a world map and tabular view.
    """

    @staticmethod
    def get(request):
        """
        Pass graph data to frontend.
        """

        first_datetime_of_update_data = DataStorage.objects.first().data_update
        last_datetime_of_update_data = DataStorage.objects.last().data_update

        worlds_students_per_country = DataStorage.worlds_students_per_country_statistics()

        datamap_format_countries_list = []
        tabular_format_countries_list = []

        all_active_students = sum(worlds_students_per_country.itervalues())

        for country, count in worlds_students_per_country.iteritems():
            student_amount_percentage = format(count/all_active_students*100, '.2f')

            # Too small percentage doesn't show real numbers. More than two numbers after point is ugly.
            if student_amount_percentage == '0.00':
                student_amount_percentage = '~0'

            if country != 'null':
                # Make data to datamap visualization format.
                datamap_format_countries_list.append([
                    str(pycountry.countries.get(alpha_2=country).alpha_3), count
                ])

                # Make data to simple table visualization format.
                tabular_format_countries_list.append((
                    pycountry.countries.get(alpha_2=country).name, count, student_amount_percentage
                ))

            else:
                # Create students without country amount.
                tabular_format_countries_list.append(('Unset', count, student_amount_percentage))

        # Sort in descending order.
        tabular_format_countries_list.sort(key=lambda row: row[1], reverse=True)

        # Workaround when there is no data for the given day.
        if not tabular_format_countries_list:
            tabular_format_countries_list.append(('Unset', 0, 0))

        context = {
            'datamap_countries_list': json.dumps(datamap_format_countries_list),
            'tabular_countries_list': tabular_format_countries_list,
            'top_country': tabular_format_countries_list[0][0],
            'countries_amount': len(tabular_format_countries_list),
            'first_datetime_of_update_data': first_datetime_of_update_data,
            'last_datetime_of_update_data': last_datetime_of_update_data
        }

        return render(request, 'graph_creator/worldmap.html', context)


class GraphsView(View):
    """
    Provides data and plot 3 main graphs:
    1. Number of students per date.
    2. Number of courses per date.
    3. Number of instances per date.
    """

    @staticmethod
    def get(request):
        """
        Pass graph data to frontend.
        """

        timeline = DataStorage.timeline()
        students, courses, instances = DataStorage.data_per_period()
        instances_count, courses_count, students_count = DataStorage.overall_counts()

        first_datetime_of_update_data = DataStorage.objects.first().data_update
        last_datetime_of_update_data = DataStorage.objects.last().data_update

        context = {
            'timeline': json.dumps(timeline),
            'students': json.dumps(students),
            'courses': json.dumps(courses),
            'instances': json.dumps(instances),
            'instances_count': instances_count,
            'courses_count': courses_count,
            'students_count': students_count,
            'first_datetime_of_update_data': first_datetime_of_update_data,
            'last_datetime_of_update_data': last_datetime_of_update_data
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

    def post(self):
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
