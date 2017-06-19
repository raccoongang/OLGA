"""
Django admin page for analytics application.
"""

from django.contrib import admin
from .models import EdxInstallation, InstallationStatistics


class EdxInstallationAdmin(admin.ModelAdmin):
    """
    Admin for edX's instances storage as EdxInstallation model with overall information.
    """
    fields = [
        'latitude',
        'longitude',
        'platform_url',
        'platform_name',
        'secret_token'
    ]


class InstallationStatisticsAdmin(admin.ModelAdmin):
    """
    Admin for edX's instances storage as InstallationStatistics model with overall information.
    """
    fields = [
        'active_students_amount_day',
        'active_students_amount_week',
        'active_students_amount_month',
        'courses_amount',
        'data_created_datetime',
        'edx_installation',
        'statistics_level',
        'students_per_country'
    ]

    readonly_fields = (
        'data_created_datetime',
    )

admin.site.register(EdxInstallation, EdxInstallationAdmin)
admin.site.register(InstallationStatistics, InstallationStatisticsAdmin)
