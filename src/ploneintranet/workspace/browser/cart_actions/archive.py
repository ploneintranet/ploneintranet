# -*- coding: utf-8 -*-
from plone import api
from ploneintranet.core import ploneintranetCoreMessageFactory as _
from ploneintranet.workspace.browser.cart_actions.base import BaseCartView


class ArchiveView(BaseCartView):
    """Archive Action implementation that uses slc.outdated to mark items as
    outdated.
    """

    def __call__(self):
        request = self.request

        pm = api.portal.get_tool('portal_membership')
        user = pm.getAuthenticatedMember()

        handled = []
        for obj in self.items:
            if not user.has_permission("slc: Toggle outdated", obj):
                api.portal.show_message(
                    message="Could not archive object '{0}': Permission "
                    "denied".format(obj.Title()),
                    request=request,
                    type="warning")
                continue
            outdated_view = obj.restrictedTraverse("object_toggle_outdated")
            outdated_view.outdated = True
            obj.reindexObject()
            handled.append(obj.Title())

        titles = ', '.join(sorted(handled))
        message = _(
            "The following items have been archived: ${titles}",
            mapping={'titles': titles}
        )
        api.portal.show_message(
            message=message,
            request=request,
            type="success",
        )

        return self.index()
