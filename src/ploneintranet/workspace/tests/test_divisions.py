# -*- coding: utf-8 -*-
from plone import api
from plone.app.testing import setRoles, login
from ploneintranet.workspace.tests.base import FunctionalBaseTestCase
from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory


vocab = 'ploneintranet.workspace.vocabularies.Divisions'


class TestDivisions(FunctionalBaseTestCase):
    """
    Test the DivisionsVocabulary
    """

    def setUp(self):
        super(TestDivisions, self).setUp()

        self.catalog = api.portal.get_tool('portal_catalog')
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
        # create a couple of divisions with the same name and description
        # to check that the vocabulary does not screw up!
        self.division_folder_1 = self.create_division(
            u"Division Workspace (™)",
            u"I ♡ unicode",
        )
        self.division_folder_2 = self.create_division(
            u"Division Workspace (™)",
            u"I ♡ unicode",
        )
        self.division_folder_3 = self.create_division(
            u"AAA I have to go first!",
        )

    def create_division(self, title, description=u''):
        ''' Create a division given a title and a description
        '''
        obj = api.content.create(
            self.workspaces,
            'ploneintranet.workspace.workspacefolder',
            title=title,
            description=description,
            is_division=True,
        )
        return obj

    def test_divisions_vocabulary(self):
        """Test that we have divisions"""
        divisions = getUtility(IVocabularyFactory, vocab)(self.portal)
        self.assertEquals(len(divisions), 3)
        observed = [(x.title, x.description) for x in divisions]
        expected = [
            (u'AAA I have to go first!', u''),
            (u'Division Workspace (\u2122)', u'I \u2661 unicode'),
            (u'Division Workspace (\u2122)', u'I \u2661 unicode')
        ]
        self.assertListEqual(observed, expected)
        observed = {(x.value, x.token) for x in divisions}
        expected = {
            (self.division_folder_1.UID(), self.division_folder_1.UID()),
            (self.division_folder_2.UID(), self.division_folder_2.UID()),
            (self.division_folder_3.UID(), self.division_folder_3.UID()),
        }
        self.assertSetEqual(observed, expected)
