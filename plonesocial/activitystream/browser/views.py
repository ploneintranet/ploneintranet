from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class StreamView(BrowserView):
    """Home page view containing activity stream viewlets."""

    index = ViewPageTemplateFile("templates/stream_view.pt")

    def render(self):
        return self.index()

    def __call__(self):
        return self.render()

    def update(self):
        """Mute plone.app.z3cform.kss.validation AttributeError"""
        pass
