from ploneintranet import api as pi_api
from ploneintranet.microblog.browser.interfaces import (
    IPloneIntranetMicroblogLayer
)


def content_statechanged(obj, event):
    """Add a status update relating to state change events"""
    if not IPloneIntranetMicroblogLayer.providedBy(obj.REQUEST):
        # We are not installed
        return

    if event.new_state.id not in ('published',):
        return

    action_verb = event.new_state.id
    # microblog_context is automatically derived from content_context
    pi_api.microblog.statusupdate.create(
        content_context=obj,
        action_verb=action_verb,
    )
