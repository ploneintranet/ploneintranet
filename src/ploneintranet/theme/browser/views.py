from zope.publisher.browser import BrowserView
from ploneintranet.theme.interfaces import IThemeSpecific


class IsThemeEnabled(BrowserView):

    def __call__(self):
        """ """
        return IThemeSpecific.providedBy(self.request)


