from Products.CMFPlone.interfaces.controlpanel import IMailSchema
from Products.Five import BrowserView
from plone.registry.interfaces import IRegistry
from zope.component import getUtility


class MailNotificationView(BrowserView):

    @property
    def mail_settings(self):
        registry = getUtility(IRegistry)
        return registry.forInterface(IMailSchema, prefix='plone')
