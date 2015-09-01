import urllib

from logging import getLogger
from plone.dexterity.utils import safe_unicode
from plone.app.contenttypes.browser import link_redirect_view
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
        _tags = [safe_unicode(t)
                 for t in ICategorization(self.context).subjects]
        return [dict(title=_tag,
                     absolute_url="%s/tag/%s" % (
                         base_url, urllib.quote(_tag.encode('utf8'))))
                for _tag in _tags]


class DownloadView(BrowserView):
    """While the library templates don't link to foofile/view
    The Plone Intranet search results do link to foofile/view.
    Catch this by a simple redirect.

    NB because of collective.documentviewer this overrides
    DXDocumentViewerView.
    """

    def __call__(self):
        self.request.response.redirect(self.context.absolute_url())


class LinkRedirectView(link_redirect_view.LinkRedirectView):
    """
    Always redirect, even if the user has edit permissions.
    (Editing is done in Barceloneta)
    """

    def __call__(self):
        return self.request.RESPONSE.redirect(self.absolute_target_url())
