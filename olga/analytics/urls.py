"""
URLs for the analytics application.
"""

from django.conf.urls import url

from . import views

app_name = 'analytics'  # pylint: disable=invalid-name

urlpatterns = [  # pylint: disable=invalid-name
    url(r'^api/token/registration/$', views.AccessTokenRegistration.as_view(), name='api_token_registration'),
    url(r'^api/token/authorization/$', views.AccessTokenAuthorization.as_view(), name='api_token_authorization'),
    url(
        r'^api/installation/statistics/$',
        views.ReceiveInstallationStatistics.as_view(),
        name='api_installation_statistics'
    )
]
