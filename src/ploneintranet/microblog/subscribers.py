from AccessControl import Unauthorized
import logging

from plone import api
from plone.uuid.interfaces import IUUID
from ploneintranet import api as pi_api
from ploneintranet.microblog.browser.interfaces import (
    IPloneIntranetMicroblogLayer
)

logger = logging.getLogger(__name__)


def content_created(obj, event):
    """Add a status update relating to content creation"""
    if not IPloneIntranetMicroblogLayer.providedBy(obj.REQUEST):
        # We are not installed
        return

    event_key = 'ploneintranet.microblog.content_created'
    enabled = obj.REQUEST.get(event_key, True)  # default is enabled
    if not enabled:
        logger.debug("%s disabled", event_key)
        return

    whitelist = ('Document', 'File', 'Image', 'News Item', 'Event')
    try:
        if obj.portal_type not in whitelist:
            return
    except AttributeError:
        return

    # microblog_context is automatically derived from content_context
    # which is why this listens to IObjectAddedEvent not IObjectCreatedEvent
    try:
        pi_api.microblog.statusupdate.create(
            content_context=obj,
            action_verb=u'created',
            tags=obj.Subject() or None,
        )
    except Unauthorized:
        # on content tree copy the IObjectAdded event is fired before the
        # child content obj is properly uuid indexed
        logger.warn("No statusupdate created for %s", obj.absolute_url())


def content_statechanged(obj, event):
    """Add a status update relating to state change events"""
    if not IPloneIntranetMicroblogLayer.providedBy(obj.REQUEST):
        # We are not installed
        return

    event_key = 'ploneintranet.microblog.content_statechanged'
    enabled = obj.REQUEST.get(event_key, True)  # default is enabled
    if not enabled:
        logger.debug("%s disabled", event_key)
        return

    whitelist = ('Document', 'File', 'Image', 'News Item', 'Event')
    try:
        if obj.portal_type not in whitelist:
            return
    except AttributeError:
        return

    if event.new_state.id not in ('published',):
        return
    action_verb = event.new_state.id
    # microblog_context is automatically derived from content_context
    pi_api.microblog.statusupdate.create(
        content_context=obj,
        action_verb=action_verb,
        tags=obj.Subject() or None,
    )


def content_removed(obj, event):
    """
    Archive all statusupdates referencing a deleted content
    object as microblog_context or content_context.
    """
    if not IPloneIntranetMicroblogLayer.providedBy(obj.REQUEST):
        # We are not installed
        return

    tool = api.portal.get_tool('ploneintranet_microblog')
    if tool.content_keys(obj) or tool.context_keys(obj):
        # obj can be already detached from parent. reconstruct url
        logger.info(
            "Archiving statusupdates referencing uuid {0} -> {1}/{2}".format(
                IUUID(obj), event.oldParent.absolute_url(), obj.id))
    for id in tool.content_keys(obj):
        tool.delete(id, restricted=False)
    for id in tool.context_keys(obj):
        tool.delete(id, restricted=False)
