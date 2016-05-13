# -*- coding: utf-8 -*-
from ploneintranet.workspace.browser.workspace import filter_users_json
from json import loads

import unittest2 as unittest


class MockUser(object):

    def __init__(self, **kwargs):
        for (k, v) in kwargs.items():
            setattr(self, k, v)

    @property
    def getId(self):
        return self.id


class TestFilterUsers(unittest.TestCase):
    users = [
        MockUser(
            Title='Alice Lindström',
            email='al@example.org',
            id='a_lindstrom',
        ),
        MockUser(
            Title='Jorge Primavera',
            email='jp@example.com',
            id='j_primavera',
        ),
    ]

    def test_filter_by_email(self):
        filtered_users = filter_users_json('@example.org', self.users)
        filtered_users_py = loads(filtered_users)
        self.assertTrue(len(filtered_users_py), 1)
        self.assertTrue(filtered_users_py[0]['id'] == 'a_lindstrom')

    def test_filter_name_uppercase(self):
        filtered_users = filter_users_json('JORGE', self.users)
        filtered_users_py = loads(filtered_users)
        self.assertTrue(len(filtered_users_py), 1)
        self.assertTrue(filtered_users_py[0]['id'] == 'j_primavera')

    def test_filter_name_unicode(self):
        filtered_users = filter_users_json(b'rö', self.users)
        filtered_users_py = loads(filtered_users)
        self.assertTrue(len(filtered_users_py), 1)
        self.assertTrue(filtered_users_py[0]['id'] == 'a_lindstrom')
