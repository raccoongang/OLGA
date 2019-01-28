"""
Helpers for the analytics part of OLGA application.
"""

import httplib
import requests
import logging

from django.http import HttpResponse

from olga.analytics.forms import (
    EdxInstallationParanoidLevelForm,
    EdxInstallationEnthusiastLevelForm,
    InstallationStatisticsParanoidLevelForm,
    InstallationStatisticsEnthusiastLevelForm
)

logging.basicConfig()

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def validate_instance_stats_forms(receive_instance_stats_method):
    """
    Check if edX overall installation info and statistics are valid with corresponding forms.

    Returns HTTP-response with status 401, that means at least one of two forms is not valid.
    """
    def wrapper(request, *args, **kwargs):
        """
        Wrapper.
        """
        paranoid_installation_form = EdxInstallationParanoidLevelForm(request.POST)
        enthusiast_installation_form = EdxInstallationEnthusiastLevelForm(request.POST)
        paranoid_statistics_form = InstallationStatisticsParanoidLevelForm(request.POST)
        enthusiast_statistics_form = InstallationStatisticsEnthusiastLevelForm(request.POST)

        statistics_level = request.POST.get('statistics_level')

        level_valid_forms = {
            'paranoid': paranoid_installation_form.is_valid() and paranoid_statistics_form.is_valid(),
            'enthusiast': enthusiast_installation_form.is_valid() and enthusiast_statistics_form.is_valid()
        }

        if level_valid_forms[statistics_level]:
            return receive_instance_stats_method(request, *args, **kwargs)

        return HttpResponse(status=httplib.UNAUTHORIZED)

    return wrapper


def get_coordinates_by_platform_city_name(city_name):
    """
    Gather coordinates by platform city name with Nominatim API.
    """
    geo_api = requests.get('https://nominatim.openstreetmap.org/search/', params={'city': city_name, 'format': 'json'})

    if geo_api.status_code == 200 and geo_api.json():
        location = geo_api.json()[0]

        return location['lat'], location['lon']

    logger.info(
        'Nominatim API status: {status}, City name: {city_name}'.format(status=geo_api.status_code, city_name=city_name)
    )
    return '', ''
