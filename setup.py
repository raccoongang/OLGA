"""
Setup for acceptor.
"""

from setuptools import setup

VERSION = "0.1.0"
DESCRIPTION = "Acceptor server which takes specific data from edx-platform and visualizes the data on the charts"


setup(
    name="acceptor",
    version=VERSION,
    description=DESCRIPTION,
    license='AGPL v3',
    install_requires=[
            'Django>=1.11',
            'pycountry>=17.1.8',
            'requests>=2.13.0',
    ],
)
