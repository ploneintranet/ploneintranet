import unittest2 as unittest

#from zope import interface
from zope.component import createObject, queryUtility
from Acquisition import aq_base, aq_parent

from Products.CMFCore.utils import getToolByName
from plone.app.testing import TEST_USER_ID, setRoles
from plone.registry.interfaces import IRegistry

from plonesocial.microblog.testing import\
    PLONESOCIAL_MICROBLOG_INTEGRATION_TESTING

from plone.app.discussion.interfaces import IConversation
from plone.app.discussion.interfaces import IComment
from plone.app.discussion.interfaces import IDiscussionSettings
#from plone.app.discussion.interfaces import IDiscussionLayer


class TestInstall(unittest.TestCase):

    layer = PLONESOCIAL_MICROBLOG_INTEGRATION_TESTING

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']

        setRoles(self.portal, TEST_USER_ID, ['Manager'])
#        interface.alsoProvides(
#            self.portal.REQUEST, IDiscussionLayer)

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

    def test_add_comment_does_not_add_statusupdate(self):
        # Allow discussion
        registry = queryUtility(IRegistry)
        settings = registry.forInterface(IDiscussionSettings)
        settings.globally_enabled = True

        # attach and initialize microblog container
        microblog = IConversation(self.portal)
        comment = createObject('plone.Comment')
        comment.text = 'Comment text'
        new_id = microblog.addComment(comment)

        # do a 'vanilla' document reply
        conversation = IConversation(self.portal.doc1)
        comment = createObject('plone.Comment')
        comment.text = 'Comment text'
        new_id = conversation.addComment(comment)
        self.assertTrue(IComment.providedBy(conversation[new_id]))
        self.assertEqual(aq_base(conversation[new_id].__parent__),
                          aq_base(conversation))
        self.assertEqual(conversation.total_comments, 1)

        # we should have only the original first status update
        self.assertEqual(microblog.total_comments, 1)
