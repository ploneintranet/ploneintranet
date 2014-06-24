from Products.Five.browser import BrowserView
from plone import api
from collective.workspace.interfaces import IWorkspace
from AccessControl import Unauthorized

from ploneintranet.workspace import MessageFactory as _


class JoinView(BrowserView):

    def __call__(self):
        if not self.context.join_policy == "self":
            raise Unauthorized("No way")

        field = "button.join"
        if self.request.method == "POST" and field in self.request.form:
            user = api.user.get_current()
            workspace = IWorkspace(self.context)
            workspace.add_to_team(user=user.getId())
            msg = u"You are a fully qualified member of this workspace now"
            api.portal.show_message(message=_(msg),
                                    request=self.request)

        referer = self.request.get("HTTP_REFERER", self.context.absolute_url())
        return self.request.response.redirect(referer)
