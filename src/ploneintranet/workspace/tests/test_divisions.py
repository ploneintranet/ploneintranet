# -*- coding: utf-8 -*-
import transaction
from plone import api
from plone.app.testing import setRoles, login

from ploneintranet.search.solr.testing import IntegrationTestCase
from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory

from ploneintranet.suite.testing import PLONEINTRANET_SUITE_SOLR_INTEGRATION

vocab = 'ploneintranet.workspace.vocabularies.Divisions'


class TestDivisions(IntegrationTestCase):
    """
    Test the DivisionsVocabulary
    """

    layer = PLONEINTRANET_SUITE_SOLR_INTEGRATION

    def setUp(self):
        super(TestDivisions, self).setUp()
        self.portal = self.layer['portal']
        self.catalog = api.portal.get_tool('portal_catalog')
        self.request = self.layer['request']

        api.user.create(username='john_doe', email='john@doe.org')
        setRoles(self.portal, 'john_doe', ['Manager', ])

        login(self.portal, 'john_doe')
        self.workspaces = api.content.create(
            self.portal,
            'ploneintranet.workspace.workspacecontainer',
            'example-workspace-container'
        )

        self.workspace_folder = api.content.create(
            self.workspaces,
            'ploneintranet.workspace.workspacefolder',
            'example-workspace'
        )
        self.division_folder = api.content.create(
            self.workspaces,
            'ploneintranet.workspace.workspacefolder',
            'division-workspace'
        )
        self.division_folder.is_division = True
        self.division_folder.title = u"Division Workspace"
        self.division_folder.reindexObject()
        transaction.commit()

    def test_divisions_vocabulary(self):
        """Test that we have divisions"""
        divisions = getUtility(IVocabularyFactory, vocab)(self.portal)

        self.assertEquals(len(divisions), 1)
