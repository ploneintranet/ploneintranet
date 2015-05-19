from ..interfaces import ITodoUtility
from Acquisition import aq_inner
from plone import api
from ploneintranet.theme.utils import dexterity_update
from ploneintranet.workspace.browser.workspace import BaseWorkspaceView
from zope.component import getUtility
from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent
from ploneintranet.theme import _


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
        modified, errors = dexterity_update(context)

        if self.workspace().is_case:
            if self.can_edit and milestone is not None \
               and milestone != context.milestone:
                context.milestone = milestone
                modified = True

        if modified:
            api.portal.show_message(
                _("Item updated."), request=self.request, type="success")
            context.reindexObject()
            notify(ObjectModifiedEvent(context))

        if errors:
                api.portal.show_message(
                    _("There was an error."),
                    request=self.request,
                    type="error",
                )

        return super(TodoView, self).__call__()
