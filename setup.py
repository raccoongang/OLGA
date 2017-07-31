"""
Setup for acceptor.
"""

from setuptools import setup

VERSION = "0.1.0"
DESCRIPTION = "OLGA server which takes specific data from edx-platform and visualizes the data on the charts"


setup(
    name="OLGA",
    version=VERSION,
    description=DESCRIPTION,
    license='AGPL v3',
    install_requires=[
        'ddt>=1.1.1',
        'Django>=1.11',
        'gunicorn>=19.7.1',
        'factory-boy==2.8.1',
        'mock==2.0.0',
        'psycopg2==2.7.1',
        'pycountry>=17.1.8',
        'requests>=2.13.0',
    ],
)
