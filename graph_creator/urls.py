"""
URLs for the graph_creator application.
"""

from django.conf.urls import url

from . import views

app_name = 'graph_creator'  # pylint: disable=invalid-name

urlpatterns = [  # pylint: disable=invalid-name
    url(r'^$', views.GraphsView.as_view(), name='charts'),
    url(r'^map/$', views.MapView.as_view(), name='map'),
    url(r'^receive/$', views.ReceiveData.as_view(), name='receive_data')
]
