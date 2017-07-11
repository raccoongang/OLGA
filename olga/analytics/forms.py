"""
Forms for received edX installation data.
"""

from django import forms

from .models import EdxInstallation, InstallationStatistics

# Pylint does not has opportunity to disable duplicate code (forms and admin has the same peaces).
# So apart from duplicate-code with `disable=all` it disables missing-docstring, too-few-public-methods and no-init.
# pylint: disable=all
# flake8: noqa=D101


class AccessTokenForm(forms.Form):
    access_token = forms.UUIDField()


class EdxInstallationForm(forms.ModelForm):
    class Meta(object):
        model = EdxInstallation
        fields = [
            'access_token',
            'platform_name',
            'platform_url',
            'latitude',
            'platform_url'
        ]


class InstallationStatisticsForm(forms.ModelForm):
    class Meta(object):
        model = InstallationStatistics
        fields = [
            'active_students_amount_day',
            'active_students_amount_week',
            'active_students_amount_month',
            'courses_amount',
            'statistics_level',
            'students_per_country'
        ]
