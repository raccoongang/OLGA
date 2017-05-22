from django.conf.urls import url

from . import views

app_name = 'graph_creator'

urlpatterns = [
    url(r'^$', views.GraphsView.as_view(), name='charts'),
    url(r'^map/$', views.MapView.as_view(), name='map'),
    url(r'^receive/$', views.ReceiveData.as_view(), name='receive_data')
]
