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

    @view.memoize
    def sections(self):
        """Return toplevel section navigation"""
        obj = self.context
        while (obj.portal_type != 'ploneintranet.library.app' and
               obj.portal_type != 'Plone Site'):
            obj = obj.aq_inner.aq_parent

        if obj.portal_type == 'Plone Site':
            log.error("Cannot find parent Library app!")
            return []

        app = obj
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
        struct = []
        for child in self.context.objectValues():
            if child.portal_type == 'ploneintranet.library.folder':
                type_ = 'container'
            elif child.portal_type in ('Document',):
                type_ = 'document'
            else:
                # to add: collection, newsitem, event, link, file
                log.error("Unsupported type %s", child.portal_type)

            section = dict(title=child.Title(),
                           description=child.Description(),
                           absolute_url=child.absolute_url(),
                           type=type_,)
            content = []
            for grandchild in child.objectValues():
                if grandchild.portal_type == 'ploneintranet.library.folder':
                    (follow, icon) = ("follow-section", "icon-squares")
                elif grandchild.portal_type in ('Document',):
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

    pass


class LibrarySectionView(LibraryListingView):

    pass


class LibraryFolderView(LibraryListingView):

    pass
