from django.contrib import admin
from .models import DataStorage


class DataStorageAdmin(admin.ModelAdmin):
    """
    Admin for edX`s instances storage.
    """
    fields = [
        'active_students_amount_day',
        'active_students_amount_week',
        'active_students_amount_month',
        'courses_amount',
        'data_update',
        'latitude',
        'longitude',
        'platform_url',
        'platform_name',
        'secret_token',
        'statistics_level',
        'students_per_country'
    ]

admin.site.register(DataStorage, DataStorageAdmin)
