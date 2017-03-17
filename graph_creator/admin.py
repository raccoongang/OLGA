from django.contrib import admin

from .models import DataStorage


class DataStorageAdmin(admin.ModelAdmin):
    fields = ['students_quantity']


admin.site.register(DataStorage, DataStorageAdmin)
