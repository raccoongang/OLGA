"""
URLs for the charts application.
"""

from django.conf.urls import url

from . import views

app_name = 'charts'  # pylint: disable=invalid-name

urlpatterns = [  # pylint: disable=invalid-name
    url(r'^$', views.GraphsView.as_view(), name='charts'),
    url(r'^map/$', views.MapView.as_view(), name='map'),
]
