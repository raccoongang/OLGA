"""
URLs for the analytics application.
"""

from django.conf.urls import url

from . import views

app_name = 'analytics'  # pylint: disable=invalid-name

urlpatterns = [  # pylint: disable=invalid-name
    url(r'^receive/$', views.ReceiveData.as_view(), name='receive_data')
]
