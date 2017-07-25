"""
URLs for the analytics application.
"""

from django.conf.urls import url

from olga.analytics import views

app_name = 'analytics'

urlpatterns = [
    url(
        r'^api/token/registration/$',
        views.AccessTokenRegistration.as_view(),
        name='api_token_registration'),

    url(
        r'^api/token/authorization/$',
        views.AccessTokenAuthorization.as_view(),
        name='api_token_authorization'),

    url(
        r'^api/installation/statistics/$',
        views.ReceiveInstallationStatistics.as_view(),
        name='api_installation_statistics'
    )
]
