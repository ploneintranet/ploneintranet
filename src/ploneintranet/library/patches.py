# -*- coding: utf-8 -*-
from OFS.interfaces import IOrderedContainer
from plone.folder.interfaces import IExplicitOrdering
from Products.CMFPlone.interfaces import IPloneSiteRoot

# The following patch for getOrdering fixes the problem that the context
# of an ordering is missing its acquisition context.
# NOTE: This patch should be removed once PR
# https://github.com/plone/plone.app.content/pull/81 has been merged
# and released.


def patched_getOrdering(self):
    if IPloneSiteRoot.providedBy(self.context):
        return self.context
    try:
        if self.context.aq_base.getOrdering():
            ordering = self.context.getOrdering()
        else:
            return None
    except AttributeError:
        if IOrderedContainer.providedBy(self.context):
            # Archetype
            return IOrderedContainer(self.context)
        return None
    if not IExplicitOrdering.providedBy(ordering):
        return None
    return ordering
