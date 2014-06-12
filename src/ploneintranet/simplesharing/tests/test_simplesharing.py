import unittest
import transaction
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.testing import z2
from ploneintranet.simplesharing.testing import \
    PLONEINTRANET_SIMPLESHARING_FUNCTIONAL_TESTING


class TestBehaviors(unittest.TestCase):

    layer = PLONEINTRANET_SIMPLESHARING_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.request = self.layer['request']

        # add our behavior to Page
        behaviors = ('ploneintranet.simplesharing.behaviors.ISimpleSharing', )
        self.portal.portal_types.Document.behaviors = behaviors
        # set the default plone workflow
        wftool = self.portal.portal_workflow
        wftool.setChainForPortalTypes(
            ['Document'],
            ['plone_workflow'],
        )
        transaction.commit()

        # prepare browser
        self.browser = z2.Browser(self.app)
        self.browser.handleErrors = False
        self.browser.addHeader(
            'Authorization',
            'Basic %s:%s' % (SITE_OWNER_NAME, SITE_OWNER_PASSWORD,)
        )
        self.browser.open('http://nohost/plone')

    def test_visibility(self):
        # create a new document
        page_link = self.browser.getLink('Page')
        page_link.click()
        visibility_control = self.browser.getControl('Visibility')
        self.assertGreater(len(visibility_control.options), 1)
        self.browser.getControl('Save').click()
