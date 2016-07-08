from OFS.CopySupport import CopyError
from ZODB.POSException import ConflictError
from ploneintranet.core import ploneintranetCoreMessageFactory as _
from ploneintranet.workspace.browser.cart_actions.base import BaseCartView

import re


class PasteView(BaseCartView):

    def __call__(self):
        self.heading = _(u'Pasted')
        try:
            self.context.manage_pasteObjects(REQUEST=self.request)
        except CopyError, ce:
            message = re.sub('<[^>]*>|\n', ' ', ce.message)
            self.message = re.sub('\s{2,}', ' ', message).strip()
        except ConflictError:
            self.message = _(u'Error while pasting items')
        else:
            self.message = _(u"Item(s) pasted")

        return self.index()
