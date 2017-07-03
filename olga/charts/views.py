"""
Views for the charts application.
"""

from datetime import datetime
import json

from django.shortcuts import render
from django.views.generic import View

from olga.analytics.models import InstallationStatistics


def get_first_and_last_datetime_of_update_data():  # pylint: disable=invalid-name
    """
    Get first and last datetimes OLGA acceptor gathers statistics.
    """
    try:
        first_datetime_of_update_data = InstallationStatistics.objects.first().data_created_datetime
        last_datetime_of_update_data = InstallationStatistics.objects.last().data_created_datetime
    except AttributeError:
        first_datetime_of_update_data = datetime.now()
        last_datetime_of_update_data = datetime.now()

    return first_datetime_of_update_data, last_datetime_of_update_data


class MapView(View):
    """
    Displays information on a world map and tabular view.
    """

    @staticmethod
    def get_statistics_top_country(tabular_format_countries_list):
        """
        Gets first country from tabular format country list.
        List is sorted, first country is a top active students rank country.
        """

        if len(tabular_format_countries_list) == 0:
            return None
        else:
            return tabular_format_countries_list[0][0]

    def get(self, request):
        """
        Passes graph data to frontend.
        """

        first_datetime_of_update_data, last_datetime_of_update_data = get_first_and_last_datetime_of_update_data()

        countries_amount, datamap_format_countries_list, tabular_format_countries_list = \
            InstallationStatistics().get_worlds_students_per_country_data_to_render()

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
    Provides data and plot 3 main graphs:
    1. Number of students per date.
    2. Number of courses per date.
    3. Number of instances per date.
    """

    @staticmethod
    def get(request):
        """
        Passes graph data to frontend.
        """

        timeline = InstallationStatistics.timeline()

        students, courses, instances = InstallationStatistics.data_per_period()

        instances_count, courses_count, students_count = InstallationStatistics.overall_counts()

        first_datetime_of_update_data, last_datetime_of_update_data = get_first_and_last_datetime_of_update_data()

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
