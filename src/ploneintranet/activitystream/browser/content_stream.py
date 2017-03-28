# coding=utf-8
from plone import api
from plone.memoize.view import memoize
from ploneintranet import api as pi_api
from Products.Five.browser import BrowserView

import logging


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
    @memoize
    def has_shares(self):
        return bool(self.num_shares)

    @property
    @memoize
    def num_shares(self):
        return len(self._statusupdates_threadparents())

    @property
    @memoize
    def has_comments(self):
        return bool(self.num_comments)

    @property
    @memoize
    def num_comments(self):
        return len([su for su in self._statusupdates_all()
                    if su.thread_id])

    @property
    @memoize
    def is_whitelisted(self):
        ''' Check if the context portal type is whitelisted
        '''
        whitelist = api.portal.get_registry_record(
            'ploneintranet.microblog.whitelisted_types',
        )
        return self.context.portal_type in whitelist

    @property
    def can_init_comments(self):
        ''' Check if we can initialize the comments here
        '''
        if self.has_shares:
            return False
        if not self.is_whitelisted:
            return False
        return True

    @memoize
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
                if su.id in reply_thread_ids or
                su is last]

    @memoize
    def _statusupdates_all(self):
        container = pi_api.microblog.get_microblog()
        return list(container.content_values(self.context))

    def show_stream(self):
        ''' Check if we should show the stream
        '''
        return self.has_shares or self.is_whitelisted

    def __call__(self):
        ''' On the content stream we want all the comments,
        because the "Show older comments" feature implemented in
        ploneintranet.prototype#390
        it is still not style for the content stream
        '''
        self.request.form['all_comments'] = 1
        return super(ContentStreamView, self).__call__()
