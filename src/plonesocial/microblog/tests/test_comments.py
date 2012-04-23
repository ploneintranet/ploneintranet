import unittest2 as unittest

from zope.component import createObject
from Acquisition import aq_base, aq_parent

from Products.CMFCore.utils import getToolByName
from plone.app.testing import TEST_USER_ID, setRoles

from plonesocial.microblog.testing import\
    PLONESOCIAL_MICROBLOG_INTEGRATION_TESTING

from plone.app.discussion.interfaces import IConversation
from plone.app.discussion.interfaces import IComment


class TestInstall(unittest.TestCase):

    layer = PLONESOCIAL_MICROBLOG_INTEGRATION_TESTING

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        typetool = self.portal.portal_types
        typetool.constructContent('Document', self.portal, 'doc1')
        self.typetool = typetool
        self.portal_discussion = getToolByName(self.portal,
                                               'portal_discussion',
                                               None)

    def test_add_statusupdate(self):
        microblog = IConversation(self.portal)
        comment = createObject('plone.Comment')
        comment.text = 'Comment text'
        new_id = microblog.addComment(comment)
        self.assertTrue(IComment.providedBy(microblog[new_id]))
        self.assertEqual(aq_base(microblog[new_id].__parent__),
                          aq_base(microblog))
        self.assertEqual(microblog.total_comments, 1)

    def test_parent_microblog(self):
        microblog = IConversation(self.portal)
        self.assertEqual(aq_parent(microblog),
                         aq_base(self.portal))
        self.assertEqual(microblog.__parent__,
                         self.portal)

    def test_parent_statusupdate(self):
        microblog = IConversation(self.portal)
        comment = createObject('plone.Comment')
        comment.text = 'Comment text'
        microblog.addComment(comment)
        self.assertEqual(aq_parent(comment),
                         aq_base(microblog))
        self.assertEqual(aq_parent(aq_parent(comment)),
                         aq_base(self.portal))
        self.assertEqual(comment.__parent__.__parent__,
                         self.portal)
