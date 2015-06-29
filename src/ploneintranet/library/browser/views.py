from logging import getLogger
from Products.Five import BrowserView
from plone import api
from plone.memoize import view

from ploneintranet.library import _

log = getLogger(__name__)


class LibraryHomeView(BrowserView):
    """
    The '/library' link in the portal tabs is coded as a CMF action
    and not derived from the actual library app URL.
    This view redirects to the, or a, actual LibraryApp/view.
    """
    def __call__(self):
        catalog = api.portal.get_tool('portal_catalog')
        results = catalog(portal_type='ploneintranet.library.app')
        if not results:
            msg = "Somebody removed the last library app and broke the site."
            log.error(msg)
            return msg
        target = results[0].getURL()

        if len(results) > 1:
            # pick the first one, unless there is one actually called 'libary'
            for brain in results:
                if brain.id == 'library':
                    target = brain.getURL()

        # get us to an actual LibraryAppView
        self.request.response.redirect(target)


class LibraryListingView(BrowserView):

    def app(self):
        return self.chain(getapp=True)

    @view.memoize
    def chain(self, getapp=False):
        _chain = []
        obj = self.context
        while (obj.portal_type != 'ploneintranet.library.app' and
               obj.portal_type != 'Plone Site'):
            _chain.insert(0, dict(title=obj.Title,
                                  absolute_url=obj.absolute_url()))
            obj = obj.aq_inner.aq_parent

        if obj.portal_type == 'Plone Site':
            raise AttributeError("Cannot find parent Library app!")

        if getapp:
            return obj
        return _chain

    @view.memoize
    def sections(self):
        """Return toplevel section navigation"""
        app = self.app()
        sections = app.objectValues()
        current_url = self.request['ACTUAL_URL']
        current_nav = app
        for s in sections:
            if current_url.startswith(s.absolute_url()):
                current_nav = s
                break

        app_current = (app == current_nav) and 'current' or ''
        menu = [dict(title=_("All topics"),
                     absolute_url=app.absolute_url(),
                     current=app_current)]

        for s in sections:
            s_current = (s == current_nav) and 'current' or ''
            menu.append(dict(title=s.Title,
                             absolute_url=s.absolute_url(),
                             current=s_current))
        return menu

    @view.memoize
    def children(self):
        """Return children and grandchildren of current context"""
        folderish = ('ploneintranet.library.section',
                     'ploneintranet.library.folder')
        pageish = ('Document', 'News Item', 'Link')

        struct = []
        for child in self.context.objectValues():
            if child.portal_type in folderish:
                type_ = 'container'
            elif child.portal_type in pageish:
                type_ = 'document'
            else:
                # to add: collection, newsitem, event, link, file
                type_ = 'unsupported'
                log.error("Unsupported type %s", child.portal_type)

            section = dict(title=child.Title(),
                           description=child.Description(),
                           absolute_url=child.absolute_url(),
                           type=type_,)
            content = []
            for grandchild in child.objectValues():
                if grandchild.portal_type in folderish:
                    (follow, icon) = ("follow-section", "icon-squares")
                elif grandchild.portal_type in pageish:
                    (follow, icon) = ("follow-page", "icon-page")
                else:
                    # to add: collection, newsitem, event, link, file
                    log.error("Unsupported type %s", grandchild.portal_type)
                    (follow, icon) = ("follow-x", "icon-x")
                content.append(dict(
                    title=grandchild.Title(),
                    absolute_url=grandchild.absolute_url(),
                    follow=follow,
                    icon=icon))
            section['content'] = content
            struct.append(section)
        return struct


class LibraryAppView(LibraryListingView):

    def info(self):
        return {}


class LibrarySectionView(LibraryListingView):

    def info(self):
        return dict(title=self.context.Title,
                    description=self.context.Description)


class LibraryFolderView(LibraryListingView):

    def info(self):
        return dict(
            chain=self.chain(),
            description=self.context.Description)
