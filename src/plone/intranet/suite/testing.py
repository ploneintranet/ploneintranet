from plone.app.testing import PloneWithPackageLayer
from plone.app.testing import IntegrationTesting
from plone.app.testing import FunctionalTesting

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
