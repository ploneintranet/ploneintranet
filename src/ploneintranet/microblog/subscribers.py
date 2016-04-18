from ploneintranet import api as pi_api
from ploneintranet.microblog.browser.interfaces import (
    IPloneIntranetMicroblogLayer
)


def content_statechanged(obj, event):
    """Add a status update relating to state change events"""
    if not IPloneIntranetMicroblogLayer.providedBy(obj.REQUEST):
        # We are not installed
        return
#    import pdb; pdb.set_trace()

    if event.new_state.id != 'published':
        return

    creator = obj.Creator()
    # microblog_context is automatically derived from content_context
    pi_api.microblog.statusupdate.create(
        obj.Title(),
        userid=creator,
        content_context=obj,
    )
