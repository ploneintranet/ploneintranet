from zope.interface import implements
from zope.component import adapts

from plone.app.discussion.interfaces import IComment
from Products.CMFCore.interfaces import IContentish
from Acquisition import aq_inner, aq_parent

from plone import api
from plonesocial.activitystream.interfaces import IStatusActivity
from plonesocial.activitystream.interfaces import IContentActivity
from plonesocial.activitystream.interfaces import IDiscussionActivity
from plonesocial.activitystream.interfaces import IActivity


class StatusActivity(object):
    # conditionally configured in zcml
    # adapts(IStatusUpdate)
    implements(IStatusActivity)

    def __init__(self, context):
        self.context = context
        self.text = context.text
        self.title = ''
        self.url = ''
        self.portal_type = 'StatusUpdate'
        self.render_type = 'status'
        self.Creator = context.creator
        self.userid = context.userid
        self.raw_date = context.date
        m_context = context.context  # IStatusUpdate.IMicroblogContext
        if m_context:
            self.title = m_context.Title()
            self.url = m_context.absolute_url()
        else:
            self.url = api.portal.get().absolute_url()

    def replies(self):
        return map(IStatusActivity, self.context.replies())


class AbstractContentActivity(object):

    def __init__(self, context):
        self.context = context
        self.title = context.Title()
        self.url = context.absolute_url()
        self.portal_type = context.portal_type
        self.Creator = context.Creator()
        self.raw_date = max(context.created(), context.effective())


class ContentActivity(AbstractContentActivity):
    adapts(IContentish)
    implements(IContentActivity)

    def __init__(self, context):
        super(ContentActivity, self).__init__(context)
        self.userid = context.getOwnerTuple()[1]
        self.render_type = 'item'
        self.text = context.Description() + self._tags(context.Subject())

    def _tags(self, source):
        return ' '.join(['#%s' % x for x in source])


class DiscussionActivity(AbstractContentActivity):
    adapts(IComment)
    implements(IDiscussionActivity)

    def __init__(self, context):
        super(DiscussionActivity, self).__init__(context)
        self.render_type = 'discussion'
        self.userid = context.author_username
        # context: DiscussionItem
        # parent: Conversation
        # grandparent: content object
        _contentparent = aq_parent(aq_parent(aq_inner(context)))
        self.title = _contentparent.Title()
        self.text = context.getText()


def brainActivityFactory(context):
    return IActivity(context.getObject())
