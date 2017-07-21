#!/usr/bin/env python

"""
Fake edX installation's requests to OLGA API. Script appends fake data to database for following analysis.

Script tests:
    - common requests flow from edX to acceptor;
    - if acceptor lost edX's access token.

Run script:
    - olga/./fake_instance.py (from directory with `manage.py`)

Also, developer can specify port (default value is 7000):
    - olga/./fake_instance.py 8000
"""

import httplib
import json
import sys
from uuid import uuid4

import requests


def make_registration_request(port):
    """
    Make registration request.

    Returns access token.
    """
    token_registration_request = requests.post(
        'http://0.0.0.0:{0}/api/token/registration/'.format(port)
    )

    access_token = token_registration_request.json()['access_token']

    return access_token


def make_authorization_request(port, access_token):
    """
    Make authorization request.
    """
    authorization_requests = requests.post(
        'http://0.0.0.0:{0}/api/token/authorization/'.format(port), data={'access_token': access_token}
    )

    return authorization_requests


def make_statistics_request(port, statistics_data):
    """
    Make statistics request.
    """
    statistics_requests = requests.post(
        'http://0.0.0.0:{0}/api/installation/statistics/'.format(port), data=statistics_data
    )

    return statistics_requests


def get_default_statistics_data(statistics_level, access_token):
    """
    Provide default instance data.
    """
    statistics_data = {
        'access_token': access_token,
        'active_students_amount_day': 20,
        'active_students_amount_week': 40,
        'active_students_amount_month': 60,
        'courses_amount': 4,
        'statistics_level': 'paranoid',
    }

    if statistics_level == 'enthusiast':
        statistics_data.update({
            'latitude': 50.10,
            'longitude': 40.05,
            'platform_name': 'platform_name',
            'platform_url': 'https://platform-url.com',
            'statistics_level': 'enthusiast',
            'students_per_country': json.dumps({'CA': 10, 'UA': 5})
        })

    return statistics_data


def fake_common_flow(port):
    """
    Fake common requests flow from edX to acceptor.
    """
    statistics_levels = ['paranoid', 'enthusiast']

    access_token = make_registration_request(port)
    authorization_request = make_authorization_request(port, access_token)

    if authorization_request.status_code == httplib.OK:

        print 'Fake new instance result:'
        for level in statistics_levels:

            statistics_data = get_default_statistics_data(level, access_token)
            statistics_request = make_statistics_request(port, statistics_data)

            if statistics_request.status_code == httplib.CREATED:
                print '    - `{0}` level is OK.'.format(level.capitalize())


def acceptor_lost_edx_token(port):
    """
    Fake requests flow if acceptor lost edX's access token.
    """
    statistics_levels = ['paranoid', 'enthusiast']

    access_token = uuid4().hex
    authorization_request = make_authorization_request(port, access_token)

    if authorization_request.status_code == httplib.UNAUTHORIZED:
        access_token = authorization_request.json()['refreshed_access_token']

        print '\nFake acceptor lost edX\'s access token:'
        for level in statistics_levels:
            statistics_data = get_default_statistics_data(level, access_token)
            statistics_request = make_statistics_request(port, statistics_data)

            if statistics_request.status_code == httplib.CREATED:
                print '    - `{0}` level is OK.'.format(level.capitalize())


def get_server_port():
    """
    Get developer's specified port, if it exists.
    """
    try:
        port = sys.argv[1]
    except IndexError:
        port = 7000

    return port


if __name__ == '__main__':
    server_port = get_server_port()

    fake_common_flow(server_port)
    acceptor_lost_edx_token(server_port)
