from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class PlonesocialView(BrowserView):
    """Plonesocial integrated home page view."""

    index = ViewPageTemplateFile("templates/plonesocial_view.pt")

    def render(self):
        return self.index()

    def __call__(self):
        return self.render()
