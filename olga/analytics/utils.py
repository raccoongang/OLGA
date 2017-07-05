"""
Helpers for the analytics part of OLGA application.
"""

from django.http import HttpResponse

from .forms import EdxInstallationForm, InstallationStatisticsForm

HTTP_401_UNAUTHORIZED = 401


def installation_statistics_forms_checker(receive_installation_statistics_post_method):  # pylint: disable=invalid-name
    """
    Checksare edX overall installation info and statistics valid with corresponding forms.

    Returns HTTP-response with status 401, that means at least one of two forms is not valid.
    """
    def receive_installation_statistics_post_method_wrapper(request, *args, **kwargs):  # pylint: disable=invalid-name
        """
        Wrapper.
        """
        edx_installation_form = EdxInstallationForm(request.POST)
        installation_statistics_form = InstallationStatisticsForm(request.POST)

        if edx_installation_form.is_valid() and installation_statistics_form.is_valid():
            return receive_installation_statistics_post_method(request, *args, **kwargs)

        return HttpResponse(status=HTTP_401_UNAUTHORIZED)

    return receive_installation_statistics_post_method_wrapper
