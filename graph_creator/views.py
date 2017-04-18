import uuid

import requests

from django.core import serializers
from django.shortcuts import render
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View
from django.utils.decorators import method_decorator
from django.urls import reverse

from .models import DataStorage


class IndexView(View):
    """
    Displays information on a world map.
    
    Retrieve information about edx-platform from DB, serialize it into JSON format and
    pass serialized data to the template. The template displays a map of the world with the
    edx-platform marker on it.
    
    `edx_data_as_json` is a `DataStorage` containing all information about edx-platform.
    
    Returns http response and passes `edx_data_as_json` data as a context variable `edx_data`
    to the `index.html` template.
    """

    def get(self, request, *args, **kwargs):
        """
        Retrieve information about edx-platform from DB and serialize it into JSON.
        
        `edx_data_as_json` is a `DataStorage` containing all information about edx-platform.
        """

        edx_data_as_json = serializers.serialize('json', DataStorage.objects.all())
        return render(request, 'graph_creator/index.html', {'edx_data': edx_data_as_json})


@method_decorator(csrf_exempt, name='dispatch')
class ReceiveData(View):
    """
    Receives and processes data from the remote edx-platform.
    
    If the platform has already registered, a normal data exchange happens.
    Otherwise generates a secret token, (registers)saves it to DB with the edx-platform's incoming URL
    and sends newly generated token to the edx-platform for further 
    data interchange abilities with the server.
    """

    def post(self, request, *args, **kwargs):
        """
        Receive information from the edx-platform and processes it.
        
        If the first time gets information from edx-platform, generates a secret token and
        sends it back to the edx-platform for further data exchange abilities, otherwise
        updates data in the DB with the new incoming information from the edx-platform.
        
        `secret_token` when generates is a uuid.UUID in string format.
        `reverse_token` is a requests. Sends the secret token to edx-platform.
        
        Returns http response redirecting to the main page.
        """

        received_data = self.request.POST
        courses_amount = received_data.get('courses_amount')
        students_amount = received_data.get('students_amount')
        latitude = received_data.get('latitude')
        longitude = received_data.get('longitude')
        platform_url = received_data.get('platform_url')
        secret_token = received_data.get('secret_token')

        if secret_token is None:
            secret_token = uuid.uuid4().hex
            DataStorage.objects.create(secret_token=secret_token, platform_url=platform_url)
            # reverse_token = requests.post(
            #     'http://192.168.1.139:8000/acceptor_data/', data={"reverse_token": secret_token}
            # )
            reverse_token = requests.post(
                str(platform_url) + '/acceptor_data/', data={"reverse_token": secret_token}
            )
        else:
            DataStorage.objects.filter(secret_token=str(secret_token)).update(
                courses_amount=int(courses_amount),
                students_amount=int(students_amount),
                latitude=float(latitude),
                longitude=float(longitude),
                platform_url=platform_url
            )

        return redirect(reverse('graph_creator:index'))
