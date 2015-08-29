import logging
from Products.Five import BrowserView

logger = logging.getLogger(__name__)


class ReindexObjectView(BrowserView):
    """
    Reindex the current object
    """

    def __call__(self):
        """ Reindex """
        logger.info("Reindexing %s", self.context.absolute_url(1))
        self.context.reindexObject()
        if '_authenticator' not in self.request:
            return "Directly calling this view does not work (plone.protect)"
        return "Object at %s has been reindexed successfully" % \
            self.context.absolute_url(1)
