"""
Views for the charts application.
"""

import json
from datetime import datetime

from django.shortcuts import render
from django.views.generic import View
from django.db.models import Max, Min

from olga.analytics.models import InstallationStatistics


def get_data_created_datetime_scope():
    """
    Get the first and last datetimes for the entire time of gathering statistics.
    """
    data_created_datetime_scope = InstallationStatistics.objects.aggregate(
        Min('data_created_datetime'), Max('data_created_datetime')
    )

    first_dt = data_created_datetime_scope['data_created_datetime__min'] or datetime.now()
    last_dt = data_created_datetime_scope['data_created_datetime__max'] or datetime.now()

    return first_dt, last_dt


class MapView(View):
    """
    Display information on a world map and tabular view.
    """

    @staticmethod
    def get_statistics_top_country(tabular_format_countries_list):
        """
        Get first country from tabular format country list.

        List is sorted, first country is a top active students rank country.
        """
        return tabular_format_countries_list[0][0]

    def get(self, request):
        """
        Pass graph data to frontend.
        """
        first_datetime_of_update_data, last_datetime_of_update_data = get_data_created_datetime_scope()

        datamap_format_countries_list, tabular_format_countries_list = \
            InstallationStatistics().get_students_per_country()

        countries_amount = InstallationStatistics().get_students_countries_amount()

        context = {
            'datamap_countries_list': json.dumps(datamap_format_countries_list),
            'tabular_countries_list': tabular_format_countries_list,
            'top_country': self.get_statistics_top_country(tabular_format_countries_list),
            'countries_amount': countries_amount,
            'first_datetime_of_update_data': first_datetime_of_update_data,
            'last_datetime_of_update_data': last_datetime_of_update_data
        }

        return render(request, 'charts/worldmap.html', context)


class GraphsView(View):
    """
    Provide data and plot 3 main graphs: number of, students, courses and instances per date.
    """

    @staticmethod
    def get(request):
        """
        Pass graph data to frontend.
        """
        timeline = InstallationStatistics.timeline()

        students, courses, instances = InstallationStatistics.data_per_period()

        instances_count, courses_count, students_count = InstallationStatistics.overall_counts()

        first_datetime_of_update_data, last_datetime_of_update_data = get_data_created_datetime_scope()

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

        return render(request, 'charts/graphs.html', context)
