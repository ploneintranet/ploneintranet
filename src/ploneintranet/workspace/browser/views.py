from Products.Five.browser import BrowserView
from plone import api
from collective.workspace.interfaces import IWorkspace
from AccessControl import Unauthorized
from plone.app.workflow.browser.sharing import SharingView as BaseSharingView

from ploneintranet.workspace import MessageFactory as _


class JoinView(BrowserView):

    def __call__(self):
        if not self.context.join_policy == "self":
            msg = _(u"Workspace join policy doesn't allow self join")
            raise Unauthorized(msg)

        field = "button.join"
        req_method = self.request.method.lower()
        if req_method == "post" and field in self.request.form:
            user = api.user.get_current()
            workspace = IWorkspace(self.context)
            workspace.add_to_team(user=user.getId())
            msg = _(u"You are a member of this workspace now")
            api.portal.show_message(message=_(msg),
                                    request=self.request)

        referer = self.request.get("HTTP_REFERER", "").strip()
        if not referer:
            referer = self.context.absolute_url()
        return self.request.response.redirect(referer)


class SharingView(BaseSharingView):
    def can_edit_inherit(self):
        return False

    def role_settings(self):
        result = super(SharingView, self).role_settings()
        uid = self.context.UID()
        return filter(lambda x: not x["id"].endswith(uid), result)
