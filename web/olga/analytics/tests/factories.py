"""
Provides factories for analytics models.
"""

import uuid
from datetime import datetime
from pytz import UTC

from factory import SubFactory
from factory.django import DjangoModelFactory


from olga.analytics.models import InstallationStatistics, EdxInstallation

# Factories are self documenting
# flake8: noqa:D101
# pylint: disable=missing-docstring, too-few-public-methods


class EdxInstallationFactory(DjangoModelFactory):
    class Meta:
        model = EdxInstallation

    access_token = uuid.uuid4().hex
    platform_name = 'platform_name'
    platform_url = 'https://platform-url.com'
    latitude = 50.10
    longitude = 40.05


class InstallationStatisticsFactory(DjangoModelFactory):
    class Meta:
        model = InstallationStatistics

    active_students_amount_day = 5
    active_students_amount_week = 10
    active_students_amount_month = 15
    courses_amount = 1
    data_created_datetime = datetime(2012, 1, 1, tzinfo=UTC)
    edx_installation = SubFactory(EdxInstallationFactory)
    statistics_level = 'enthusiast'
    students_per_country = {"RU": 2632, "CA": 18543, "UA": 2011, "null": 1}
