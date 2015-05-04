from plone import api
from ploneintranet.activitystream.interfaces import IStatusActivity
from zope.interface import implements


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
