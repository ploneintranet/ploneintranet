import unittest2 as unittest

#from zope.component import createObject
#from Acquisition import aq_base, aq_parent
#from Products.CMFCore.utils import getToolByName
from plone.app.testing import TEST_USER_ID, setRoles

from plonesocial.microblog.testing import\
    PLONESOCIAL_MICROBLOG_INTEGRATION_TESTING

from plonesocial.microblog.statusupdate import StatusUpdate
from plonesocial.microblog.interfaces import IStatusContainer


class TestStatusContainer(unittest.TestCase):

    layer = PLONESOCIAL_MICROBLOG_INTEGRATION_TESTING

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def test_wrapping(self):
        container = IStatusContainer(self.portal)
