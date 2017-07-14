"""
Helpers for the analytics part of OLGA application.
"""

import httplib

from django.http import HttpResponse

from .forms import EdxInstallationForm, InstallationStatisticsForm


def validate_instance_stats_forms(receive_instance_stats_method):
    """
    Check if edX overall installation info and statistics are valid with corresponding forms.

    Returns HTTP-response with status 401, that means at least one of two forms is not valid.
    """
    def wrapper(request, *args, **kwargs):
        """
        Wrapper.
        """
        edx_installation_form = EdxInstallationForm(request.POST)
        installation_statistics_form = InstallationStatisticsForm(request.POST)

        if edx_installation_form.is_valid() and installation_statistics_form.is_valid():
            return receive_instance_stats_method(request, *args, **kwargs)

        return HttpResponse(status=httplib.UNAUTHORIZED)

    return wrapper
