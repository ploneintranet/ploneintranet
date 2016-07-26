# -*- coding: utf-8 -*-
# flake8: noqa
from plone.api.validation import required_parameters
from ploneintranet.microblog.interfaces import IMicroblogContext
from ploneintranet.microblog.interfaces import IMicroblogTool
from ploneintranet.network.interfaces import INetworkTool
from zope.component import queryUtility
from zope.globalrequest import getRequest

import statusupdate

event_keys = (
    'ploneintranet.microblog.content_created',
    'ploneintranet.microblog.content_statechanged'
)



def get_microblog():
    ''' Get the microblog utility

    :returns: microblog utility
    :rtype: object
    '''
    return queryUtility(IMicroblogTool)


def get_network():
    ''' Get the network utility

    :returns: network utility
    :rtype: object
    '''
    return queryUtility(INetworkTool)


def get_microblog_context(
    context,
):
    """Get the microblog context

    :param context: [required] The context for which
        we want the microblog context.
        Can be None.
    :type context: object

    :returns: microblog context
    :rtype: object

    :raises:
        MissingParameterError
        InvalidParameterError
    """
    if context is None:
        return None

    # context is part of context.aq_chain
    # but unittests do not always wrap acquisition
    if IMicroblogContext.providedBy(context):
        return context
    try:
        chain = context.aq_inner.aq_chain
    except AttributeError:
        return None

    for item in chain:
        if IMicroblogContext.providedBy(item):
            return item
    else:
        return None

def events_disable(request=None):
    """Temporarily disable event-driven statusupdate creation for this request.

    :param request: The request for which events are to be disabled
    :type request: Request
    """
    if not request:
        request = getRequest()
    if not request:
        return
    for event_key in event_keys:
        request[event_key] = False


def events_enable(request=None):
    """Re-enable event-driven statusupdate creation for this request.
    This only makes sense if you explicitly disabled statusupdate creation,
    since it is enabled by default.

    :param request: The request for which events were disabled
    :type request: Request
    """
    if not request:
        request = getRequest()
    if not request:
        return
    for event_key in event_keys:
        request[event_key] = True
