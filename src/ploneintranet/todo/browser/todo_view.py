from ..interfaces import ITodoUtility
from Acquisition import aq_inner
from plone import api
from ploneintranet.workspace.browser.workspace import BaseWorkspaceView
from zope.component import getUtility
from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent


class BaseView(BaseWorkspaceView):

    def __init__(self, context, request):
        super(BaseView, self).__init__(context, request)
        self.util = getUtility(ITodoUtility)
        self.current_user_id = api.user.get_current().getId()
        self.content_uid = api.content.get_uuid(self.context)


class TodoView(BaseView):

    def __call__(self, milestone=None):
        context = aq_inner(self.context)
        self.can_edit = api.user.has_permission(
            'Modify portal content', obj=context)

        if self.workspace().is_case:
            if self.can_edit and milestone is not None \
               and milestone != context.milestone:
                context.milestone = milestone
                context.reindexObject()
                notify(ObjectModifiedEvent(context))

        return super(TodoView, self).__call__()
