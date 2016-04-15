# coding=utf-8
from plone import api
from ploneintranet.layout.testing import IntegrationTestCase


class TestViews(IntegrationTestCase):

    def setUp(self):
        ''' Custom shared utility setup for tests.
        '''
        self.portal = self.layer['portal']
        self.request = self.layer['request']

    def test_date_picker_i18n_json(self):
        ''' We want pat-date-picker i18n
        '''
        view = api.content.get_view(
            'date-picker-i18n.json',
            self.portal,
            self.request,
        )
        self.assertTrue("January" in view())
