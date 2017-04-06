import requests
import uuid

from django.core import serializers
from django.shortcuts import render
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View
from django.utils.decorators import method_decorator
from django.urls import reverse
from .models import DataStorage


class IndexView(View):
    def get(self, request, *args, **kwargs):
        edx_data_as_json = serializers.serialize('json', DataStorage.objects.all())
        return render(request, 'graph_creator/index.html', {'edx_data': edx_data_as_json})


@method_decorator(csrf_exempt, name='dispatch')
class ReceiveData(View):
    """
    This view receives data from the remote edx-platform.
    If the platform has already registered, a normal data exchange happens.
    Otherwise we generate a secret token, save it to DB with the edx-platform incoming URL
    and send newly generated token to the edx-platform for further registration
    and data interchange abilities with the server.
    """
    def post(self, request, *args, **kwargs):

        received_data = self.request.POST
        courses_amount = received_data.get('courses_amount')
        students_amount = received_data.get('students_amount')
        latitude = received_data.get('latitude')
        longitude = received_data.get('longitude')
        platform_url = received_data.get('platform_url')
        secret_token = received_data.get('secret_token')

        if secret_token is None:
            secret_token = uuid.uuid4().hex
            obj = DataStorage.objects.create()
            obj.secret_token = secret_token
            obj.platform_url = platform_url
            obj.save()
            reverse_token = requests.post('http://192.168.1.139:8000/acceptor_data/',
                                          data={"reverse_token": secret_token})
        else:
            obj = DataStorage.objects.get(secret_token=str(secret_token))
            obj.courses_amount = int(courses_amount)
            obj.students_amount = int(students_amount)
            obj.latitude = float(latitude)
            obj.longitude = float(longitude)
            obj.platform_url = platform_url
            obj.save()

        return redirect(reverse('graph_creator:index'))
