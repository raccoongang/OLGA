from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views.generic import View
from django.shortcuts import redirect
from django.urls import reverse
from .models import DataStorage


class IndexView(View):

    def get(self, request, *args, **kwargs):
        students_quantity, created = DataStorage.objects.get_or_create(pk=1)
        return render(request, 'graph_creator/index.html', {'students_quantity': students_quantity})


@method_decorator(csrf_exempt, name='dispatch')
class ReceiveData(View):
    def post(self, request, *args, **kwargs):
        received_data = int(self.request.POST.get('number_of_students'))
        obj, created = DataStorage.objects.get_or_create(pk=1)
        obj.students_quantity = received_data
        obj.save()
        return redirect(reverse('graph_creator:index'))
