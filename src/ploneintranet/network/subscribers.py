import logging

from ploneintranet.network.behaviors.metadata import IDublinCore

log = logging.getLogger(__name__)


def tag_subjects(context, event):
    """
    We can resolve a UUID and store subjects as tags
    only after a new content item has been added to it's container.
    """
    wrapped = IDublinCore(context, None)
    if wrapped:  # only if the behavior is enabled
        # re-setting subjects should now trigger graph.tag()
        wrapped.subjects = context.subject
