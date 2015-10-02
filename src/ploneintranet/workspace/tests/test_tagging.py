# coding=utf-8
from plone import api
from ploneintranet.workspace.basecontent import utils
from ploneintranet.workspace.interfaces import IWorkspaceAppFormLayer
from ploneintranet.workspace.testing import \
    PLONEINTRANET_WORKSPACE_INTEGRATION_TESTING
from ploneintranet.workspace.tests.base import BaseTestCase
from zope.interface import alsoProvides


class TestTagging(BaseTestCase):
    """ Test that a comma separated string of tabs is saved as a tuple of
    strings
    """
    layer = PLONEINTRANET_WORKSPACE_INTEGRATION_TESTING

    def setUp(self):
        super(TestTagging, self).setUp()
        alsoProvides(self.request, IWorkspaceAppFormLayer)
        workspaces = self.portal["workspaces"]
        self.ws = api.content.create(
            workspaces,
            'ploneintranet.workspace.workspacefolder',
            'test-tag-workspace',
            title='Test Tag Workspace',
        )
        self.doc = api.content.create(
            self.ws,
            'Document',
            'tagged-doc',
            'Tagged Document',
        )

    def tearDown(self):
        super(TestTagging, self).tearDown()
        api.content.delete(obj=self.ws)

    def test_set_multiple_tags(self):
        """Set multiple tags on an object as a comma separated string and
        verify that they are saved as a tuple of strings."""
        self.request.form['subjects'] = u'a,b,c'
        utils.dexterity_update(self.doc, self.request)
        self.assertEqual((u'a', u'b', u'c'), self.doc.subject)

    def test_set_multiple_tags_utf8(self):
        """Set multiple tags on an object as a comma separated string and
        verify that they are saved as a tuple of strings."""
        self.request.form['subjects'] = u'a ♥,b,c'
        utils.dexterity_update(self.doc, self.request)
        self.assertEqual((u'a ♥', u'b', u'c'), self.doc.subject)
