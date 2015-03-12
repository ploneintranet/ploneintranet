from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets.common import ViewletBase


class SimpleSharingViewlet(ViewletBase):
    """
    Viewlet to display the simple sharing form
    """
    index = ViewPageTemplateFile('sharing.pt')
