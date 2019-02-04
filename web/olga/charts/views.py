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
    def get(request):
        """
        Pass graph data to frontend.
        """
        context = {
            'months': json.dumps(InstallationStatistics().get_students_per_country()),
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

        first_datetime_of_update_data, last_datetime_of_update_data = get_data_created_datetime_scope()

        charts = InstallationStatistics.get_charts_data()

        context = {
            'timeline': json.dumps(timeline),
            'students': json.dumps(students),
            'courses': json.dumps(courses),
            'instances': json.dumps(instances),
            'first_datetime_of_update_data': first_datetime_of_update_data,
            'last_datetime_of_update_data': last_datetime_of_update_data,
            'charts': json.dumps(charts),
        }

        # Update context with this data: instances_count, courses_count, students_count, generated_certificates_count
        context.update(InstallationStatistics.overall_counts())

        return render(request, 'charts/graphs.html', context)
