from plone import api
from plone.uuid.interfaces import IUUID
from Products.Five import BrowserView
from zope.component import getUtility

from ..interfaces import ITodoUtility
from ..interfaces import MUST_READ


class MarkRead(BrowserView):

    def __call__(self):
        todos = getUtility(ITodoUtility)
        current_user = api.user.get_current()
        todos.complete_action(
            content_uid=IUUID(self.context),
            verb=MUST_READ,
            userids=[current_user.getId()]
        )
        referer = self.request.get_header("referer")
        # We must rerender the page we came from to get the value
        # for pat-inject.
        # We rerender the whole page here which is not quite smart
        self.request.response.redirect(referer)
