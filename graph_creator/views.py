import json
import requests
import uuid

from django.core import serializers
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views.generic import View
from django.shortcuts import redirect
from django.urls import reverse
from .models import DataStorage


class IndexView(View):
    def get(self, request, *args, **kwargs):
        edx_data_as_json = serializers.serialize('json', DataStorage.objects.all())
        return render(request, 'graph_creator/index.html', {'edx_data': edx_data_as_json})


@method_decorator(csrf_exempt, name='dispatch')
class ReceiveData(View):
    def post(self, request, *args, **kwargs):

        # Receiving data
        received_data = self.request.POST
        courses_amount = received_data.get('courses_amount')
        students_amount = received_data.get('students_amount')
        latitude = received_data.get('latitude')
        longitude = received_data.get('longitude')
        platform_url = received_data.get('platform_url')
        secret_token = received_data.get('secret_token')

        # Saving data
        obj, created = DataStorage.objects.get_or_create(pk=1)
        obj.courses_amount = int(courses_amount)
        obj.students_amount = int(students_amount)
        obj.latitude = float(latitude)
        obj.longitude = float(longitude)
        obj.platform_url = platform_url
        if obj.secret_token is secret_token:
            obj.save()
        else:
            secret_token = uuid.uuid4()
            obj.secret_token = secret_token
            obj.save()
            reverse_token = requests.post('http://requestb.in/11n3rhx1', data={"reverse_token": secret_token})

        return redirect(reverse('graph_creator:index'))
