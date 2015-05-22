from zope.interface import implements
from Products.CMFCore.utils import UniqueObject
from Products.CMFCore.utils import getToolByName
from OFS.SimpleItem import SimpleItem

from interfaces import IMicroblogTool
from interfaces import IMicroblogContext
from statuscontainer import QueuedStatusContainer


class MicroblogTool(UniqueObject, SimpleItem, QueuedStatusContainer):
    """Provide IStatusContainer as a site utility."""

    implements(IMicroblogTool)

    meta_type = 'ploneintranet.microblog tool'
    id = 'ploneintranet_microblog'

    # FIXME this method is called a lot - view.memoize or performance optimize
    def allowed_status_keys(self):
        """Return the subset of IStatusUpdate keys
        that are related to UUIDs of accessible contexts.
        I.e. blacklist all IStatusUpdate that has a context
        which we don't have permission to access.

        This method is implemented on the tool,
        overriding a noop implementation on BaseStatusContainer.

        This implementation depends on two critical assumptions:

        1) The set of available IMicroblogContext objects can be
        adequately queried from the catalog. This implies a reliance
        on the "View" permission - any workspace that should not be
        accessible should not have View.

        This assumption is currently violated by workspace. FIXME.

        2) The global security manager is valid.
        This is currently OK but would be violated if we were to
        introduce nested workspaces.
        Even though non-nested workspaces already introduce a local
        security manager, this only applies to content *within* the
        workspace. The security of the workspace itself is adequately
        reflected in the global security manager.
        """
        catalog = getToolByName(self, 'portal_catalog')
        marker = IMicroblogContext.__identifier__

        # microblog backend access control completely relies on this:
        # catalog implicitly filters on current_user View permission
        results = catalog.searchResults(object_provides=marker)

        # SiteRoot context is NOT whitelisted
        whitelist = [x.UID for x in results]
        # SiteRoot context is not UUID indexed, so not blacklisted
        blacklist = [x for x in self._uuid_mapping.keys()
                     if x not in whitelist]

        # return all statuses with no IMicroblogContext (= SiteRoot)
        # or with a IMicroblogContext that is accessible (= not blacklisted)
        return self._allowed_status_keys(blacklist)
