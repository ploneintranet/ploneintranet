import urllib

from logging import getLogger
from plone.memoize import view
from Products.Five import BrowserView

from ploneintranet.library.browser import utils
from ploneintranet.library.browser.views import LibraryBaseView
from ploneintranet.network.behaviors.metadata import ICategorization


log = getLogger(__name__)


class ContentView(LibraryBaseView):

    @view.memoize
    def parent(self):
        return self.context.aq_parent

    @view.memoize
    def siblings(self):
        return utils.children_of(self.context.aq_parent)

    @view.memoize
    def subjects(self):
        base_url = self.app().absolute_url()
        return [dict(title=tag,
                     absolute_url="%s/tag/%s" % (base_url, urllib.quote(tag)))
                for tag in ICategorization(self.context).subjects]


class DownloadView(BrowserView):
    """While the library templates don't link to foofile/view
    The Plone Intranet search results do link to foofile/view.
    Catch this by a simple redirect.

    NB because of collective.documentviewer this overrides
    DXDocumentViewerView.
    """

    def __call__(self):
        self.request.response.redirect(self.context.absolute_url())
