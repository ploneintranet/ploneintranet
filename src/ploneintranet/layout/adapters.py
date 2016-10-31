from Products.CMFCore.interfaces import ISiteRoot
from zope.interface import implementer
from .interfaces import IAppContent, IAppContainer


@implementer(IAppContent)
class AppContent(object):

    def __init__(self, context):
        self.context = context

    @property
    def app_name(self):
        return getattr(self.get_app(), 'app_name', '')

    @property
    def in_app(self):
        return bool(self.get_app())

    def get_app(self):
        if IAppContainer.providedBy(self.context):
            return self.context
        else:
            for item in self.context.aq_chain:
                if IAppContainer.providedBy(item):
                    return item
                elif ISiteRoot.providedBy(item):
                    return None
        return None
