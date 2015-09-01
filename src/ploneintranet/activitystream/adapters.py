# coding=utf-8
from plone import api
from ploneintranet.activitystream.interfaces import IStatusActivity
from zope.interface import implementer


@implementer(IStatusActivity)
class StatusActivity(object):

    def __init__(self, context):
        self.context = context
        self.getId = context.getId()
        self.text = context.text
        self.title = ''
        self.url = ''
        self.portal_type = 'StatusUpdate'
        self.render_type = 'status'
        self.Creator = context.creator
        self.userid = context.userid
        self.raw_date = context.date
        m_context = context.microblog_context
        if m_context:
            self.title = m_context.Title()
            self.url = m_context.absolute_url()
        else:
            self.url = api.portal.get().absolute_url()

    def replies(self):
        """ The replies to this StatusActivity as StatusActivity
        """
        return map(IStatusActivity, self.context.replies())
