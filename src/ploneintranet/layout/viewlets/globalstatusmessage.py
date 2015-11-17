from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage
from plone.app.layout.viewlets.common import ViewletBase
from ploneintranet.core import ploneintranetCoreMessageFactory as _  # noqa
from plone.i18n.normalizer import idnormalizer


class GlobalStatusMessage(ViewletBase):
    """ Displays messages to the current user.
        The markup is changed to rely on pat-notification.
    """
    index = ViewPageTemplateFile('globalstatusmessage.pt')

    def update(self):
        super(GlobalStatusMessage, self).update()
        self.status = IStatusMessage(self.request)
        messages = self.status.show()
        for m in messages:
            m.id = idnormalizer.normalize(m.message)
        self.messages = messages
        self.closetext = _(u"button_close", default=u"Close")
