# -*- coding: utf-8 -*-
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from datetime import datetime
from plone import api
from plone.memoize.view import memoize
from plone.tiles import Tile
from plonesocial.microblog.interfaces import IMicroblogTool
from plonesocial.microblog.statusupdate import StatusUpdate
from plonesocial.microblog.utils import get_microblog_context
from zope.component import queryUtility
try:
    from ploneintranet.attachments.attachments import IAttachmentStoragable
    from ploneintranet.attachments.utils import extract_and_add_attachments
except ImportError:
    IAttachmentStoragable = None
    extract_and_add_attachments = None


class NewPostBoxTile(Tile):

    index = ViewPageTemplateFile('templates/new-post-box-tile.pt')
    is_attachment_supported = True

    input_prefix = 'form.widgets.'
    button_prefix = 'form.buttons.'

    @property
    @memoize
    def post_container(self):
        ''' Return the object that will contain the post
        '''
        return queryUtility(IMicroblogTool)

    @property
    @memoize
    def post_context(self):
        ''' The context of this microblog post
        (the portal, a workspace, and so on...)
        '''
        return get_microblog_context(self.context)

    @property
    @memoize
    def is_posting(self):
        ''' Check if the form was submitted
        '''
        return ('%sstatusupdate' % self.button_prefix) in self.request.form

    @property
    @memoize
    def post_text(self):
        ''' The text that was posted
        '''
        return self.request.form.get(('%stext' % self.input_prefix), u'')

    @property
    @memoize
    def post_attachment(self):
        '''
        The attachmented that was posted (if any)
        '''
        return self.request.form.get(
            ('%sattachments' % self.input_prefix),
            None
        )

    @property
    @memoize
    def thread_id(self):
        ''' Return the thread_id
        (used e.g. for commenting other status updates)
        '''
        if hasattr(self.context, 'thread_id') and self.context.thread_id:
            thread_id = self.context.thread_id  # threaded
        elif isinstance(self.context, StatusUpdate):
            thread_id = self.context.id  # first reply
        else:
            thread_id = None  # new
        return thread_id

    def create_post_attachment(self, post):
        ''' Check:
         - if the post supports attachments
         - if we have an attachment posted

        If both are True attach the data to the post
        '''
        if IAttachmentStoragable is None:
            return
        if not IAttachmentStoragable.providedBy(post):
            return
        if not self.post_attachment:
            return
        token = self.request.get('attachment-form-token')
        extract_and_add_attachments(
            self.post_attachment,
            post,
            workspace=self.context,
            token=token
        )

    def create_post(self):
        ''' Return the post object or None
        '''
        if not self.post_text:
            return None
        post = StatusUpdate(
            self.post_text,
            context=self.post_context,
            thread_id=self.thread_id
        )
        self.create_post_attachment(post)
        self.post_container.add(post)
        return post

    @property
    @memoize
    def attachment_form_token(self):
        """ Set up a token used in the attachment form
        """
        member = api.user.get_current()
        username = member.getUserName()
        return "{0}-{1}".format(
            username,
            datetime.utcnow().strftime('%Y%m%d%H%M%S%f')
        )

    def update(self):
        ''' When updating we may want to process the form data and,
        if needed, create a post
        '''
        if self.is_posting:
            self.post = self.create_post()
        else:
            self.post = None
        # BBB attachment_form_token is already a property
        # of the view, no need to define a form
        # In order to get rid of the next line we have to remove any reference
        # to the form in the template
        self.form = {'attachment_form_token': self.attachment_form_token}

    def __call__(self, *args, **kwargs):
        ''' Call the multiadapter update

        We need to call the update manually (Tile instances don't do it)
        '''
        self.update()
        return super(NewPostBoxTile, self).__call__(*args, **kwargs)

    ###
    # The following properties are currently set to dummy values.
    # Reason: We want the template to already mirror the Prototype;
    # this includes various conditions based on the following properties

    @property
    @memoize
    def user(self):
        return u"test_user"

    @property
    @memoize
    def direct(self):
        return False

    @property
    @memoize
    def hideuser(self):
        return False

    @property
    @memoize
    def fixeduser(self):
        return False

    @property
    @memoize
    def placeholder(self):
        return u"What are you doing?"
