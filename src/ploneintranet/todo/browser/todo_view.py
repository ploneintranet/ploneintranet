from ..interfaces import ITodoUtility
from Acquisition import aq_inner
from Products.Five import BrowserView
from plone import api
from ploneintranet.workspace.interfaces import IMetroMap
from ploneintranet.workspace.utils import parent_workspace
from zope.component import getUtility
from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent


class BaseView(BrowserView):

    def __init__(self, context, request):
        super(BaseView, self).__init__(context, request)
        self.util = getUtility(ITodoUtility)
        self.current_user_id = api.user.get_current().getId()
        self.content_uid = api.content.get_uuid(self.context)

    def __call__(self):
        referer = self.request.get('HTTP_REFERER', '').strip()
        if not referer:
            referer = self.context.absolute_url()
        return self.request.response.redirect(referer)


class TodoView(BaseView):
    def __call__(self, milestone=None):
        context = aq_inner(self.context)
        self.can_edit = api.user.has_permission('Modify portal content', obj=context)

        self.workspace = parent_workspace(context)
        if self.workspace.is_case:
            if milestone is not None:
                context.milestone = milestone
                context.reindexObject()
                notify(ObjectModifiedEvent(context))

            self.milestones = IMetroMap(self.workspace).metromap_sequence.keys()

        return super(BaseView, self).__call__()
