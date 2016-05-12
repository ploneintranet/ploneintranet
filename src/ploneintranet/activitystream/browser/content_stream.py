# coding=utf-8
import logging
from Products.Five.browser import BrowserView
from plone import api
from ploneintranet import api as pi_api


logger = logging.getLogger('ploneintranet.activitystream')


class ContentStreamView(BrowserView):
    """This view renders a conversation on a content object
    i.e. document discussion.
    """

    def statusupdate_views(self):
        """Return all toplevel (non-reply) statusupdates (shares)
        on this document, wrapped in a StatusUpdateView.
        The toplevel views themselves render the comments inline by
        delegating to helper views.
        """
        for statusupdate in self._statusupdates_threadparents():
            yield api.content.get_view(
                'content-share.html',
                statusupdate,
                self.request
            )

    @property
    def has_shares(self):
        return bool(self.num_shares)

    @property
    def num_shares(self):
        return len(self._statusupdates_threadparents())

    @property
    def num_comments(self):
        return len([su for su in self._statusupdates_all()
                    if su.thread_id])

    def _statusupdates_threadparents(self):
        """Render all shares, except when it's an older share
        without any replies.
        """
        toplevels = []
        reply_thread_ids = []
        for su in self._statusupdates_all():
            if not su.thread_id:
                toplevels.append(su)
            else:
                reply_thread_ids.append(su.thread_id)
        if not toplevels:
            return []
        last = toplevels[-1]
        # show only toplevels with replies + most recent toplevel
        # i.e. suppress earlier toplevels without replies
        return [su for su in toplevels
                if su.id in reply_thread_ids
                or su is last]

    def _statusupdates_all(self):
        container = pi_api.microblog.get_microblog()
        return container.content_values(self.context)
