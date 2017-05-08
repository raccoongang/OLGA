# coding=utf-8
"""
Tests for graph_creator application views.
"""


from ddt import ddt, data, unpack

from django.test import TestCase

from graph_creator.views import ReceiveData


@ddt
class StudentsWithoutCountryTest(TestCase):
    """
    Tests for views-method `update_students_without_no_country_value`, that calculates amount of students,
    that have no country.
    """

    @data(
        # (Amount of students per country, Active students amount, Expected result)
        (
            [
                {u'count': 0, u'country': None},
                {u'count': 1, u'country': u'UA'},
                {u'count': 1, u'country': u'RU'}
            ], 3, 1
        ),
        (
            [
                {u'count': 0, u'country': None},
                {u'count': 45, u'country': u'UA'},
                {u'count': 13, u'country': u'RU'}
            ], 60, 2
        )
    )
    @unpack
    def test_correct_result_returned_from_update_students_without_no_country_value(
            self, students_per_country, active_students_amount, expected_result):

        native_data_students_per_country = ReceiveData.update_students_without_no_country_value(
            active_students_amount, students_per_country
        )

        self.assertEqual(native_data_students_per_country[0]['count'], expected_result)
