from ..interfaces import ITodoUtility
from Acquisition import aq_inner
from logging import getLogger
from plone import api
from plone.app.blocks.interfaces import IBlocksTransformEnabled
from ploneintranet.core import ploneintranetCoreMessageFactory as _  # noqa
from ploneintranet.workspace.basecontent.baseviews import ContentView
from ploneintranet.workspace.basecontent.utils import dexterity_update
from ploneintranet.workspace.utils import parent_workspace
from zope.component import getUtility
from zope.event import notify
from zope.interface import implementer
from zope.lifecycleevent import ObjectModifiedEvent

log = getLogger(__name__)


class BaseView(ContentView):

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
        self.workspace = parent_workspace(context)

        if self.workspace.is_case:
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

    def update(self):
        """ """
        if ('task_action' in self.request and
                not self.request.get('form.submitted')):
            task_action = self.request.get('task_action')
            if task_action == 'close':
                api.content.transition(
                    obj=self.context,
                    transition='finish'
                )
            elif task_action == 'reopen':
                self.context.reopen()
            api.portal.show_message(_(
                'Changes applied'), request=self.request,
                type="success")
        super(TodoView, self).update()
