from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets import globalstatusmessage


class GlobalStatusMessage(globalstatusmessage.GlobalStatusMessage):
    """ Displays messages to the current user.
        The markup is changed to rely on pat-notification.
    """
    index = ViewPageTemplateFile('globalstatusmessage.pt')
