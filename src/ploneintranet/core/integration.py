# -*- coding: utf-8 -*-
from zope.component import queryUtility
from ploneintranet.microblog.interfaces import IMicroblogTool
from ploneintranet.microblog.utils import get_microblog_context
from ploneintranet.network.interfaces import INetworkTool


class PloneIntranetIntegration(object):
    """Provide runtime utility lookup that does not throw
    ImportErrors if some components are not installed."""

    @property
    def microblog(self):
        return queryUtility(IMicroblogTool)

    @property
    def network(self):
        return queryUtility(INetworkTool)

    def context(self, context):
        return get_microblog_context(context)


PLONEINTRANET = PloneIntranetIntegration()
