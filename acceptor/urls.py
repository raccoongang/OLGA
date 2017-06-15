"""
Acceptor URL Configuration.
"""

from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [  # pylint: disable=invalid-name
    url(r'^admin/', admin.site.urls),
    url(r'^', include('edx_global_analytics.charts.urls')),
    url(r'^', include('edx_global_analytics.analytics.urls')),
]
