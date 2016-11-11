import logging

from ploneintranet.network.behaviors.metadata import IDublinCore
from zope.component.interfaces import ComponentLookupError

log = logging.getLogger(__name__)


def tag_subjects(context, event):
    """
    We can resolve a UUID and store subjects as tags
    only after a new content item has been added to it's container.
    """
    wrapped = IDublinCore(context, None)
    if wrapped:  # only if the behavior is enabled
        # re-setting subjects should now trigger graph.tag()
        try:
            wrapped.subjects = context.subject
        except ComponentLookupError:
            # this subscriber is agressively listening installation-wide but
            # ploneintranet.network is not properly loaded, e.g. in tests
            log.error("ploneintranet.network not installed")
            pass
