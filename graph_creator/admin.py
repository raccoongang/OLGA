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
        'longitude',
        'platform_url',
        'secret_token',
        'platform_name'
    ]

admin.site.register(DataStorage, DataStorageAdmin)
