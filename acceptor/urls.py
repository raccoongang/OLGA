"""
Acceptor URL Configuration.
"""

from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [  # pylint: disable=invalid-name
    url(r'^admin/', admin.site.urls),
    url(r'^stats/', include('charts.urls')),
    url(r'^', include('analytics.urls')),
]
