from ..interfaces import ITodoUtility
from Acquisition import aq_inner
from logging import getLogger
from plone import api
from plone.app.blocks.interfaces import IBlocksTransformEnabled
from ploneintranet.theme import _
from ploneintranet.theme.utils import dexterity_update
from ploneintranet.workspace.browser.workspace import BaseWorkspaceView
from zope.component import getUtility
from zope.event import notify
from zope.interface import implementer
from zope.lifecycleevent import ObjectModifiedEvent

log = getLogger(__name__)


class BaseView(BaseWorkspaceView):

    def __init__(self, context, request):
        super(BaseView, self).__init__(context, request)
        self.util = getUtility(ITodoUtility)
        self.current_user_id = api.user.get_current().getId()
        self.content_uid = api.content.get_uuid(self.context)


@implementer(IBlocksTransformEnabled)
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
                _("Your changes have been saved."),
                request=self.request,
                type="success",
            )
            context.reindexObject()
            notify(ObjectModifiedEvent(context))

        if errors:
            api.portal.show_message(
                _("There was an error."), request=self.request, type="error")

        return super(TodoView, self).__call__()

    def member_prefill(self, field):
        users = self.workspace().existing_users()
        field_value = getattr(self.context, field)
        # log.error("{0}: field_value: {1}".format(field, field_value))
        if field_value:
            assigned_users = field_value.split(',')
            return ", ".join([
                user['id']
                for user in users
                if user['id'] in assigned_users
            ])
        else:
            return ''
