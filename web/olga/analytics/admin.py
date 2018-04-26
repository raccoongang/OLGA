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
        'access_token',
        'latitude',
        'longitude',
        'platform_url',
        'platform_name',
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

    list_display = ('platform_name', 'statistics_level')

    readonly_fields = (
        'data_created_datetime',
    )

    def get_queryset(self, request):
        """
        Get queryset for the list view.

        Overriding the queriset for the admin list view of the InstallationStatistics
        """
        return super(InstallationStatisticsAdmin, self).get_queryset(request).order_by(
            'edx_installation__platform_name'
        )

    @staticmethod
    def platform_name(obj):
        """
        Return the platform_name field of the related edx_installation object.
        """
        return obj.edx_installation.platform_name


admin.site.register(EdxInstallation, EdxInstallationAdmin)
admin.site.register(InstallationStatistics, InstallationStatisticsAdmin)
