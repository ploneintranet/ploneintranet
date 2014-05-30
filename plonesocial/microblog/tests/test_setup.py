import unittest2 as unittest

from plone import api
from plone.browserlayer.utils import registered_layers

from plonesocial.microblog.testing import\
    PLONESOCIAL_MICROBLOG_INTEGRATION_TESTING

PROJECTNAME = 'plonesocial.microblog'
CSS = (
    '++resource++plonesocial.microblog.stylesheets/microblog.css',
)
PERMISSIONS = (
    'Plone Social: Add Microblog Status Update',
    'Plone Social: View Microblog Status Update',
)


class TestInstall(unittest.TestCase):

    layer = PLONESOCIAL_MICROBLOG_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']

    def test_product_is_installed(self):
        qi = self.portal['portal_quickinstaller']
        self.assertTrue(qi.isProductInstalled(PROJECTNAME))

    def test_addon_layer(self):
        layers = [l.getName() for l in registered_layers()]
        self.assertIn('IPlonesocialMicroblogLayer', layers)

    def test_cssregistry(self):
        resource_ids = self.portal.portal_css.getResourceIds()
        for id in CSS:
            self.assertIn(id, resource_ids, '{0} not installed'.format(id))

    def test_permissions(self):
        expected = ['Manager', 'Member', 'Site Administrator']
        for permission in PERMISSIONS:
            roles = self.portal.rolesOfPermission(permission)
            roles = [r['name'] for r in roles if r['selected']]
            self.assertListEqual(roles, expected)


class TestUninstall(unittest.TestCase):

    layer = PLONESOCIAL_MICROBLOG_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.qi = self.portal['portal_quickinstaller']
        with api.env.adopt_roles(['Manager']):
            self.qi.uninstallProducts(products=[PROJECTNAME])

    def test_uninstalled(self):
        self.assertFalse(self.qi.isProductInstalled(PROJECTNAME))

    def test_addon_layer_removed(self):
        layers = [l.getName() for l in registered_layers()]
        self.assertNotIn('IPlonesocialMicroblogLayer', layers)

    def test_cssregistry_removed(self):
        resource_ids = self.portal.portal_css.getResourceIds()
        for id in CSS:
            self.assertNotIn(id, resource_ids, '{0} not removed'.format(id))
