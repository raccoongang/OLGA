"""
Views for the charts application.
"""

from __future__ import division
import json

import pycountry

from django.shortcuts import render
from django.views.generic import View

from analytics.models import InstallationStatistics


class MapView(View):
    """
    Displays information on a world map and tabular view.
    """

    @staticmethod
    def get(request):
        """
        Pass graph data to frontend.
        """

        first_datetime_of_update_data = InstallationStatistics.objects.first().data_created_datetime
        last_datetime_of_update_data = InstallationStatistics.objects.last().data_created_datetime

        worlds_students_per_country = InstallationStatistics.worlds_students_per_country_statistics()

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

            # Unset is not a country
            countries_amount = 0

        else:
            # Delete unset country point from list
            countries_amount = len(tabular_format_countries_list) - 1

        context = {
            'datamap_countries_list': json.dumps(datamap_format_countries_list),
            'tabular_countries_list': tabular_format_countries_list,
            'top_country': tabular_format_countries_list[0][0],
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
        Pass graph data to frontend.
        """

        timeline = InstallationStatistics.timeline()
        students, courses, instances = InstallationStatistics.data_per_period()
        instances_count, courses_count, students_count = InstallationStatistics.overall_counts()

        first_datetime_of_update_data = InstallationStatistics.objects.first().data_created_datetime
        last_datetime_of_update_data = InstallationStatistics.objects.last().data_created_datetime

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
