from OFS.CopySupport import CopyError
from ZODB.POSException import ConflictError
from plone import api
from ploneintranet.core import ploneintranetCoreMessageFactory as _
from ploneintranet.workspace.browser.cart_actions.base import BaseCartView
from zope.component import getMultiAdapter

import re


class PasteView(BaseCartView):

    def __call__(self):
        try:
            self.context.manage_pasteObjects(REQUEST=self.request)
        except CopyError, ce:
            message = re.sub('<[^>]*>|\n', ' ', ce.message)
            message = re.sub('\s{2,}', ' ', message).strip()
            api.portal.show_message(
                message=message,
                request=self.request,
                type="warning",
            )
        except ConflictError:
            api.portal.show_message(
                message=_(u'Error while pasting items'),
                request=self.request,
                type="error",
            )
        else:
            api.portal.show_message(
                message=_(u"Item(s) pasted"),
                request=self.request,
                type="success",
            )
        return getMultiAdapter(
            (self.context, self.request), name='sidebar.default')()
