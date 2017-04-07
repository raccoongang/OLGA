from django.conf.urls import url

from . import views

app_name = 'graph_creator'
urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^receive/$', views.ReceiveData.as_view(), name='receive_data'),
]
