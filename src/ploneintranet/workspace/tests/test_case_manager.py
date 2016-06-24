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

    def get_view(self, options={}):
        ''' Get a fresh @@case-manager view
        adding options to the request
        '''
        request = self.request.clone()
        request.form.update(options)
        return api.content.get_view(
            'case-manager',
            self.portal,
            request,
        )

    def test_review_states_select(self):
        ''' Check if the review state select is configured properly
        '''
        case_manager = self.get_view()
        self.assertTupleEqual(
            case_manager.get_states(),
            (u'new', u'pending', u'published', u'rejected', u'frozen'),
        )

    def test_batching(self):
        ''' Check if the review state select is configured properly
        '''
        case_manager = self.get_view()
        self.assertEqual(case_manager.batch_size, 5)
        self.assertEqual(case_manager.batch_start, 0)
        case_manager.cases = lambda: range(4)
        self.assertEqual(
            case_manager.next_batch_url,
            ''
        )
        case_manager = self.get_view()
        case_manager.cases = lambda: range(5)
        self.assertEqual(
            case_manager.next_batch_url,
            'http://localhost:55001/plone/@@case-manager?b_start=5'
        )
        case_manager = self.get_view()
        case_manager.cases = lambda: range(6)
        self.assertEqual(
            case_manager.next_batch_url,
            'http://localhost:55001/plone/@@case-manager?b_start=5'
        )
