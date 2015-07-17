from ploneintranet import api as pi_api
from ploneintranet.microblog.browser.interfaces import (
    IPloneIntranetMicroblogLayer
)


def content_published(obj, event):
    """Add a status update relating to published events"""
    if not IPloneIntranetMicroblogLayer.providedBy(obj.REQUEST):
        # We are not installed
        return

    if event.new_state.id != 'published':
        return

    creator = obj.Creator()
    mb_context = pi_api.microblog.get_microblog_context(obj)
    pi_api.microblog.statusupdate.create(
        obj.Title(),
        userid=creator,
        microblog_context=mb_context,
        content=obj,
    )
