from ..interfaces import ITodoUtility
from logging import getLogger
from plone import api
from plone.app.blocks.interfaces import IBlocksTransformEnabled
from ploneintranet.core import ploneintranetCoreMessageFactory as _  # noqa
from ploneintranet.workspace.basecontent.baseviews import ContentView
from zope.component import getUtility
from zope.interface import implementer

log = getLogger(__name__)


class BaseView(ContentView):

    def __init__(self, context, request):
        super(BaseView, self).__init__(context, request)
        self.util = getUtility(ITodoUtility)
        self.current_user_id = api.user.get_current().getId()
        self.content_uid = api.content.get_uuid(self.context)


@implementer(IBlocksTransformEnabled)
class TodoView(BaseView):

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
