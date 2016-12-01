# -*- coding: utf-8 -*-
from collective.mustread.behaviors.maybe import IMaybeMustRead
from collective.mustread.behaviors.track import ITrackReadEnabled
from plone import api
from plone.app.testing import login
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.behavior.interfaces import IBehaviorAssignable
from ploneintranet.news.testing import IntegrationTestCase

PROJECTNAME = 'ploneintranet.news'


class InstallTestCase(IntegrationTestCase):

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']

    def test_installed(self):
        qi = self.portal['portal_quickinstaller']
        self.assertTrue(qi.isProductInstalled(PROJECTNAME))

    def test_app_installed(self):
        self.assertIn('news', self.portal)

    def test_section_installed(self):
        self.assertTrue(len(self.portal.news.sections()) > 0)

    def test_mustread_installed(self):
        qi = self.portal['portal_quickinstaller']
        self.assertTrue(qi.isProductInstalled('collective.mustread'))

    def test_mustread_behaviors_installed(self):
        login(self.portal, TEST_USER_NAME)
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        item = api.content.create(type='News Item',
                                  title='foo',
                                  container=self.portal.news)
        assignable = IBehaviorAssignable(item)
        active = [x.interface for x in assignable.enumerateBehaviors()]
        self.assertTrue(IMaybeMustRead in active)
        self.assertTrue(ITrackReadEnabled in active)


class UninstallTestCase(IntegrationTestCase):

    def setUp(self):
        self.portal = self.layer['portal']
        self.qi = self.portal['portal_quickinstaller']

        with api.env.adopt_roles(['Manager']):
            self.qi.uninstallProducts(products=[PROJECTNAME])

    def test_uninstalled(self):
        self.assertFalse(self.qi.isProductInstalled(PROJECTNAME))

    def test_app_removed(self):
        self.assertNotIn('news', self.portal)

    # mustread is uninstalled from the suite uninstall handler
