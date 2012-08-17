from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from zope.i18nmessageid import MessageFactory
_ = MessageFactory('plonesocial.activitystream')


class StreamView(BrowserView):
    """Standalone view, providing
    - microblog input
    - activitystream rendering (via stream provider)

    @@stream -> either: all activities, or
             -> my network activities (if plonesocial.network is installed)
    @@stream/explore -> all activities (if plonesocial.network is installed)
    @@stream/tag/foobar -> all activities tagged #foobar
    """

    index = ViewPageTemplateFile("templates/stream.pt")

    def render(self):
        return self.index()

    def __call__(self):
        return self.render()

    def update(self):
        """Mute plone.app.z3cform.kss.validation AttributeError"""
        pass
