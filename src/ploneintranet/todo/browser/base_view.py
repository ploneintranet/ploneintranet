from plone import api
from plone.uuid.interfaces import IUUID
from Products.Five import BrowserView
from zope.component import getUtility

from ..interfaces import ITodoUtility


class BaseView(BrowserView):

    def __init__(self, context, request):
        super(BaseView, self).__init__(context, request)
        self.util = getUtility(ITodoUtility)
        self.current_user_id = api.user.get_current().getId()
        self.content_uid = IUUID(self.context),

    def __call__(self):
        referer = self.request.get('HTTP_REFERER', '').strip()
        if not referer:
            referer = self.context.absolute_url()
        return self.request.response.redirect(referer)