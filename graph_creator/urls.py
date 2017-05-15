from django.conf.urls import url

from . import views

app_name = 'graph_creator'
urlpatterns = [
    url(r'^$', views.MapView.as_view(), name='index'),
    url(r'^receive/$', views.ReceiveData.as_view(), name='receive_data'),
    url(r'^graphs/$', views.GraphsView.as_view(), name='graphs'),
    url(r'^map/$', views.MapView.as_view(), name='map')
]
