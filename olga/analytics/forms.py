"""
Forms for received edX installation data.
"""

from django import forms
from .models import EdxInstallation, InstallationStatistics


class AccessTokenForm(forms.Form):
    access_token = forms.UUIDField()


class EdxInstallationForm(forms.ModelForm):
    class Meta:
        model = EdxInstallation
        fields = [
            'access_token',
            'platform_name',
            'platform_url',
            'latitude',
            'platform_url'
        ]


class InstallationStatisticsForm(forms.ModelForm):
    class Meta:
        model = InstallationStatistics
        fields = [
            'active_students_amount_day',
            'active_students_amount_week',
            'active_students_amount_month',
            'courses_amount',
            'statistics_level',
            'students_per_country'
        ]
