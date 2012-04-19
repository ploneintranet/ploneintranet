from zope.component import queryUtility

from plone.registry.interfaces import IRegistry

from Acquisition import aq_base
from Acquisition import aq_chain
from Acquisition import aq_inner

from Products.CMFCore.utils import getToolByName
from Products.CMFCore.interfaces import IFolderish

from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.CMFPlone.interfaces import INonStructuralFolder

from plone.app.discussion.interfaces import IDiscussionSettings


class ConversationView(object):

    def enabled(self):
        """ Returns True if discussion is enabled for this conversation.

        Used only against the SiteRoot.
        """
        return True
