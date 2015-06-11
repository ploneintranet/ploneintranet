# -*- coding: utf-8 -*-
from plone import api
# from ploneintranet.suite.testing import PLONEINTRANET_SUITE_FUNCTIONAL
from ploneintranet.suite.testing import PLONEINTRANET_SUITE_INTEGRATION
from ploneintranet.suite.uninstall import ADDITIONAL_DEPENDENCIES
import unittest2 as unittest


class TestSetup(unittest.TestCase):
    """Test that ploneintranet.suite is properly installed."""

    layer = PLONEINTRANET_SUITE_INTEGRATION

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')

    def test_product_installed(self):
        """Test if ploneintranet.suite is installed."""
        self.assertTrue(
            self.installer.isProductInstalled('ploneintranet.suite'))

    def test_dependencies_are_installed(self):
        dependencies = []
        qi = self.installer
        install_profile = qi.getInstallProfile('ploneintranet.suite')
        for dependency in install_profile.get('dependencies', ()):
            dependency = dependency.split('profile-')[-1]
            dependency = dependency.split(':')[0]
            dependencies.append(str(dependency))
        for dependency in dependencies:
            self.assertTrue(qi.isProductInstalled(dependency))
        for depdendency in ADDITIONAL_DEPENDENCIES:
            self.assertTrue(qi.isProductInstalled(dependency))


class TestUninstall(unittest.TestCase):
    """Test that ploneintranet.suite is properly uninstalled."""

    layer = PLONEINTRANET_SUITE_INTEGRATION

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')
        self.installer.uninstallProducts(['ploneintranet.suite'])

    def test_uninstall(self):
        """Test if ploneintranet.suite is cleanly uninstalled."""
        self.assertFalse(
            self.installer.isProductInstalled('ploneintranet.suite'))

    def test_dependencies_are_uninstalled(self):
        """Test if deps from the ploneintranet-namespace are uninstalled.
        Also some additional deps should be uninstalled.
        """
        dependencies = []
        qi = self.installer
        install_profile = qi.getInstallProfile('ploneintranet.suite')
        for dependency in install_profile.get('dependencies', ()):
            dependency = dependency.split('profile-')[-1]
            dependency = dependency.split(':')[0]
            dependencies.append(str(dependency))
        for dependency in dependencies:
            if dependency.startswith('ploneintranet.'):
                self.assertFalse(
                    qi.isProductInstalled(dependency),
                    '%s is still installed' % dependency)
            elif dependency not in ADDITIONAL_DEPENDENCIES:
                self.assertTrue(
                    qi.isProductInstalled(dependency),
                    '%s should not be uninstalled' % dependency)
        for depdendency in ADDITIONAL_DEPENDENCIES:
            self.assertFalse(
                qi.isProductInstalled(dependency),
                '%s is still installed' % dependency)
