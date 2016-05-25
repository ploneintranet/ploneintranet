from AccessControl import Unauthorized
from Products.Five.browser import BrowserView
from plone import api
from zope.component import queryUtility
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse

from ploneintranet.microblog.interfaces import IMicroblogTool


@implementer(IPublishTraverse)
class StatusUpdateTraverse(BrowserView):
    """Registered as a browser view at '/statusupdate/'.

    Get statusupdate.id and helper view name from the url,
    check security, and display that helper view.

    For example, /statusupdate/12345/post-menu.html will display
    post-menu.html for the statusupdate with id 12345.

    This is needed because /ploneintranet-microblog/ is not traversable
    and we want to keep it that way.
    """

    # do not allow just any view traversal
    supported_views = [
        'post-menu.html',
        'panel-delete-post.html',
        'panel-edit-post.html',
        'panel-edit-tags.html',  # not implemented yet
        'panel-edit-mentions.html',  # not implemented yet
    ]

    def publishTraverse(self, request, name):
        self.status_id = name
        stack = request.get('TraversalRequestNameStack')
        self.view_name = stack.pop()
        # stop traversing, we have arrived
        request['TraversalRequestNameStack'] = []
        # return self so the publisher calls this view
        return self

    def __call__(self):
        # do the permission checks here, now that Zope has set
        # up the security context. It can't be checked in __init__
        # because the security manager isn't set up on traverse
        container = queryUtility(IMicroblogTool)
        # get() is secure. Throws KeyError or Unauthorized on hack attempts.
        statusupdate = container.get(self.status_id)

        # block a gazillion ./absolute_url ./copy etc views
        if self.view_name not in self.supported_views:
            raise Unauthorized(self.view_name)

        # if you can access this view and the statusupdate
        # you are also allowed to access the helper views
        # any edit/delete actions are guarded in the backend anyway
        try:
            view = api.content.get_view(self.view_name,
                                        statusupdate,
                                        self.request)
            return view()
        except api.exc.InvalidParameterError:
            # this only ever happens when your code is broken
            # and typically masks another exception - go pdb here
            raise AttributeError(self.view_name)
