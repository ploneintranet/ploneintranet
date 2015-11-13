import unittest2 as unittest
from ploneintranet.workspace.browser.case_manager import percent_complete


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
