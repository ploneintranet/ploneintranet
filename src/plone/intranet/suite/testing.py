from plone.app.robotframework.testing import AUTOLOGIN_LIBRARY_FIXTURE
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneWithPackageLayer
from plone.testing import z2

import plone.intranet.suite


PLONE_INTRANET_SUITE = PloneWithPackageLayer(
    zcml_package=plone.intranet.suite,
    zcml_filename='testing.zcml',
    gs_profile_id='plone.intranet.suite:testing',
    name="PLONE_INTRANET_SUITE")

PLONE_INTRANET_SUITE_INTEGRATION = IntegrationTesting(
    bases=(PLONE_INTRANET_SUITE, ),
    name="PLONE_INTRANET_SUITE_INTEGRATION")

PLONE_INTRANET_SUITE_FUNCTIONAL = FunctionalTesting(
    bases=(PLONE_INTRANET_SUITE, ),
    name="PLONE_INTRANET_SUITE_FUNCTIONAL")

PLONE_INTRANET_SUITE_ROBOT = FunctionalTesting(
    bases=(PLONE_INTRANET_SUITE, AUTOLOGIN_LIBRARY_FIXTURE, z2.ZSERVER_FIXTURE),
    name="PLONE_INTRANET_SUITE_ROBOT")
