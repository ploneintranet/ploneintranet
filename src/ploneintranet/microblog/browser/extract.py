# coding=utf-8
from plone import api
from ploneintranet import api as piapi
from ploneintranet.core import ploneintranetCoreMessageFactory as _
from Products.CMFPlone.utils import safe_unicode
from Products.Five.browser import BrowserView
from plone.protect.interfaces import IDisableCSRFProtection
from zope.interface import alsoProvides
from zope.component import queryUtility
from ploneintranet.microblog.interfaces import IMicroblogTool
from ploneintranet.microblog.interfaces import IMicroblogContext
from zope.lifecycleevent import ObjectModifiedEvent
from zope.event import notify

import logging


logger = logging.getLogger(__name__)


class ExtractAttachments(BrowserView):
    """Extract stream attachments and dump them into an INCOMING
    folder of the corresponding workspace.

    Skips global attachments without a microblog_context.
    Skips inline replies that already have a content_context.
    """

    # turn this into a registry fetcher @property if you want to
    # customize it per client
    incoming_folder_id = _(u'INCOMING')
    incoming_folder_title = _(u'INCOMING')

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.statuscontainer = queryUtility(IMicroblogTool)
        # for the duration of the current request only
        piapi.events.disable_microblog(self.request)

    def __call__(self):
        # The worst that can happen is that an attacker tricks
        # you into running this conversion. Duh.
        alsoProvides(self.request, IDisableCSRFProtection)
        num_attachments = self.extract()
        return 'Extracted {} attachments.'.format(num_attachments)

    def extract(self):
        num_attachments = 0
        for su in self.get_statusupdates():
            for filename in su.attachments.keys():
                self.extract_attachment(su, filename)
                num_attachments += 1
        return num_attachments

    def get_statusupdates(self):
        for su in self.statuscontainer.values(limit=None):
            if not su.microblog_context:
                # skip global updates, where would we put the files?
                continue
            if IMicroblogContext.providedBy(self.context) and \
               su.microblog_context != self.context:
                # We're applying this non-optimized filter instead of
                # querying for statuscontainer.context_values() to ease
                # unittesting. It's not like this is run every minute.
                continue
            if su.content_context:
                # don't detach existing content context
                continue
            if su.thread_id:
                # don't move a reply out of it's thread, nor move the thread
                continue
            # this one we do want do process
            yield su

    def get_or_create_incoming_folder(self, su):
        if self.incoming_folder_id in su.microblog_context:
            return su.microblog_context[self.incoming_folder_id]
        else:
            return api.content.create(
                su.microblog_context, 'Folder',
                self.incoming_folder_id, self.incoming_folder_title)

    def extract_attachment(self, su, filename):
        namedfile = su.attachments.get(filename)
        if hasattr(namedfile, 'file'):
            _type = 'file'
        else:
            _type = 'image'

        # file=namedfile.file | image=namedfile.image
        data = {_type: getattr(namedfile, _type)}

        folder = self.get_or_create_incoming_folder(su)
        title = safe_unicode(filename).encode('utf8')

        # events are fired too soon
        piapi.events.disable_solr_indexing(self.request)
        piapi.events.disable_previews(self.request)

        # instead of specifying the id and running into unicode errors
        # we specify the title and let plone.api derive a safe id
        # which wil also avoid name collisions
        content = api.content.create(
            folder, _type.capitalize(), title=title, **data)
        self.apply_metadata(su, content)

        # re-enable handlers and re-fire event
        piapi.events.enable_solr_indexing(self.request)
        piapi.events.enable_previews(self.request)
        # this will trigger reindex
        notify(ObjectModifiedEvent(content))
        # but we need to regenerate the previews manually since
        # the request does not have a form.file
        if not api.env.test_mode():  # manually tested OK
            piapi.previews.generate_previews(content)
            try:
                api.content.transition(content, 'publish')
            except api.exc.InvalidParameterError:
                logger.error("Cannot publish {}".format(repr(content)))

        logger.info("Extracted {}".format(repr(content)))

        # cleanup the statusupdate
        su.attachments.remove(filename)
        # attach the new content context
        assert su.thread_id is None  # not moving a whole thread!
        su._init_content_context(su.thread_id, content)

        self.reindex_statusupdate(su)

    def apply_metadata(self, su, content):
        content.setCreators(su.creator)
        content.creation_date = su.date
        user = api.user.get(su.creator).getUser()
        content.changeOwnership(user)  # which does not seem to work, hence:
        content.manage_setLocalRoles(su.creator, ["Owner", ])
        content.reindexObjectSecurity()

    def reindex_statusupdate(self, su):
        self.statuscontainer._idx_content_context(su)
        # for good measure, though untested
        self.statuscontainer._unidx_is_content(su)
        self.statuscontainer._idx_is_content(su)
