from zope.interface import implements
from Products.CMFCore.utils import UniqueObject
from Products.CMFCore.utils import getToolByName
from OFS.SimpleItem import SimpleItem
from plone.uuid.interfaces import IUUID

from interfaces import IMicroblogTool
from interfaces import IMicroblogContext
from statuscontainer import QueuedStatusContainer


class MicroblogTool(UniqueObject, SimpleItem, QueuedStatusContainer):
    """Provide IStatusContainer as a site utility."""

    implements(IMicroblogTool)

    meta_type = 'plonesocial.microblog tool'
    id = 'plonesocial_microblog'

    def allowed_status_keys(self):
        """Return the subset of IStatusUpdate keys
        that are related to UUIDs of accessible contexts.
        I.e. blacklist all IStatusUpdate that has a context
        which we don't have permission to access.

        This method is implemented on the tool,
        overriding a noop implementation on BaseStatusContainer.
        """
        catalog = getToolByName(self, 'portal_catalog')
        marker = IMicroblogContext.__identifier__
        results = catalog.searchResults(object_provides=marker)
        # SiteRoot context is NOT whitelisted
        whitelist = [IUUID(x.getObject()) for x in results]
        # SiteRoot context is not UUID indexed, so not blacklisted
        blacklist = [x for x in self._uuid_mapping.keys()
                     if x not in whitelist]
        # return all statuses with no IMicroblogContext (= SiteRoot)
        # or with a IMicroblogContext that is accessible (= not blacklisted)
        return self._allowed_status_keys(blacklist)
