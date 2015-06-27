from logging import getLogger
from Products.Five import BrowserView
from plone import api
from plone.memoize import view


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
    def struct(self):
        """Return sections and section children"""
        struct = []
        for child in self.context.objectValues():
            section = dict(title=child.Title(),
                           description=child.Description(),
                           absolute_url=child.absolute_url())
            content = []
            for grandchild in child.objectValues():
                if grandchild.portal_type == 'ploneintranet.library.folder':
                    (follow, icon) = ("follow-section", "icon-squares")
                elif grandchild.portal_type == 'ploneintranet.library.page':
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
