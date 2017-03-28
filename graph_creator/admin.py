from django.contrib import admin

from .models import DataStorage


class DataStorageAdmin(admin.ModelAdmin):
    fields = ['courses_amount', 'students_amount', 'latitude', 'longitude']

admin.site.register(DataStorage, DataStorageAdmin)
