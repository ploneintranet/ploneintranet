# coding=utf-8
from plone import api
from ploneintranet.workspace.browser.case_manager import percent_complete
from ploneintranet.workspace.tests.base import FunctionalBaseTestCase

import unittest2 as unittest


class TestCasePercentComplete(unittest.TestCase):

    def test_half_complete(self):
        task_details = {
            'new': [{'checked': False}],
            'in_progress': [{'checked': True}, {'checked': False}],
            'decided': [{'checked': True}],
        }
        self.assertEquals(percent_complete(task_details), "50%")

    def test_third_complete(self):
        task_details = {
            'new': [{'checked': False}],
            'in_progress': [{'checked': True}, {'checked': False}],
        }
        self.assertEquals(percent_complete(task_details), "33%")

    def test_no_tasks(self):
        task_details = {}
        self.assertEquals(percent_complete(task_details), "")


class TestCaseManagerView(FunctionalBaseTestCase):

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]

    def test_review_states_select(self):
        ''' Check if the review state select is configured properly
        '''
        case_manager = api.content.get_view(
            'case-manager',
            self.portal,
            self.request,
        )
        self.assertTupleEqual(
            case_manager.get_states(),
            (u'new', u'pending', u'published', u'rejected'),
        )
