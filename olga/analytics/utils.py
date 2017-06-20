# pylint: disable-all

"""
Utilities, that create test data for charts and map.
Needed to be deleted in production as well as `olga/analytics/test_fixture.json`.

How to. From `olga/analytics` folder run:
- python utils.py
- python ../../manage.py loaddata test_fixture.json
- reload page.
"""

import datetime
import json
from random import random


class LoadTestModel(object):
    """
    Model that describes test data

    end_date is always today.
    """

    # clusters of instances
    clusters = {
        "small": {
            'courses': (1, 10),
            'students': (1, 1000),
            'quantity': (1, 100),
        },
        "middle": {
            'courses': (10, 50),  # min / max
            'students': (500, 2500),
            'quantity': 10,
        },
        "large": {
            'courses': (50, 150),
            'students': (2500, 10000),
            'quantity': (1, 100),
        },
    }

    # history of data
    days = 600

    # probability to send data per day per instance
    send_data = 0.95

    @classmethod
    def probability_to_add_course(cls):
        return probability(
            0.5 * (cls.clusters['middle']['courses'][0] + cls.clusters['middle']['courses'][1])/cls.days
        )

    @classmethod
    def probability_to_add_student(cls):
        return probability(
            0.5 * (cls.clusters['middle']['students'][0] + cls.clusters['middle']['students'][1])/cls.days
        )


def probability(x):
    return random() < x


def generate_model():

    cl = LoadTestModel()
    # for middle cluster

    instance_list = []
    number_of_instances = cl.clusters['middle']['quantity']

    instance_dict = {}
    students_dict = {}

    for instance_num in range(number_of_instances):
        for day in range(cl.days):
            if probability(cl.send_data):
                dt = (datetime.datetime.today() - datetime.timedelta(days=cl.days - day)).strftime('%Y-%m-%dT%H:%M:%SZ')

                if cl.probability_to_add_course:
                    instance_dict[instance_num] = instance_dict.get(instance_num, 0) + 1
                    students_dict[instance_num] = students_dict.get(instance_num, 0) + 25

                courses = instance_dict.get(instance_num, 0)

                if cl.probability_to_add_student:
                    students_dict[instance_num] = students_dict.get(instance_num, 0) + 0

                students = students_dict.get(instance_num, 0)

                pk = instance_num * cl.days + day

                edx_installation = {
                    "model": "analytics.edxinstallation",
                    "pk": pk,
                    "fields": {
                        "secret_token": "platform" + " " + str(instance_num),
                        "latitude": 1.0,
                        "longitude": 1.0,
                        "platform_name": "test",
                        "platform_url": "test",
                    }
                }

                installation_statistics = {
                    "model": "analytics.installationstatistics",
                    "pk": pk,
                    "fields": {
                        "active_students_amount_day": students,
                        "active_students_amount_week": 1000,
                        "active_students_amount_month": 1000,
                        "courses_amount": courses,
                        "data_created_datetime": dt,
                        "edx_installation": pk,
                        "statistics_level": 1,
                        "students_per_country": "{\"RU\": 2632, \"CA\": 18543, \"UA\": 2011, \"null\": 1}"
                    }
                }

                instance_list.append(installation_statistics)
                instance_list.append(edx_installation)

    return json.dumps(instance_list)

if __name__ == '__main__':

    data = generate_model()
    f = open('test_fixture.json', 'w')
    f.write(data)
    f.close()
