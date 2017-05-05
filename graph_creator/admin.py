from django.contrib import admin
from .models import DataStorage


class DataStorageAdmin(admin.ModelAdmin):
    """
    Admin for edX`s instances storage.
    """
    fields = [
        'courses_amount',
        'active_students_amount',
        'latitude',
        'level',
        'longitude',
        'platform_url',
        'secret_token',
        'students_per_country',
        'platform_name',
        'update'
    ]

admin.site.register(DataStorage, DataStorageAdmin)
