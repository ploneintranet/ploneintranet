from logging import getLogger
from plone.memoize import view

from ploneintranet.library.browser import utils
from ploneintranet.library.browser.views import LibraryBaseView

log = getLogger(__name__)


class ContentView(LibraryBaseView):

    @view.memoize
    def parent(self):
        return self.context.aq_parent

    @view.memoize
    def siblings(self):
        return utils.children_of(self.context.aq_parent)
