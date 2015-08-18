# -*- coding: utf-8 -*-
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from datetime import datetime
from logging import getLogger
from plone import api
from plone.memoize.view import memoize
from plone.tiles import Tile
from ploneintranet.activitystream.interfaces import IStatusActivity
from ploneintranet import api as piapi
from ploneintranet.attachments.attachments import IAttachmentStoragable
from ploneintranet.attachments.utils import extract_and_add_attachments
from ploneintranet.core import ploneintranetCoreMessageFactory as _
from ploneintranet.microblog.statusupdate import StatusUpdate

logger = getLogger('newpostbox')


class NewPostBoxTile(Tile):

    index = ViewPageTemplateFile('templates/new-post-box-tile.pt')

    input_prefix = 'form.widgets.'
    button_prefix = 'form.buttons.'

    def activity_as_post(self, activity):
        ''' BBB: just for testing
        '''
        return api.content.get_view(
            'activity_view',
            activity.context,
            self.request
        ).as_post()

    @property
    @memoize
    def post_container(self):
        """ Return the object that will contain the post
        """
        return piapi.microblog.get_microblog()

    @property
    @memoize
    def post_context(self):
        """ The context of this microblog post
        (the portal, a workspace, and so on...)
        """
        return piapi.microblog.get_microblog_context(self.context)

    @property
    @memoize
    def is_posting(self):
        """ Check if the form was submitted
        """
        return ('%sstatusupdate' % self.button_prefix) in self.request.form

    @property
    @memoize
    def post_text(self):
        """ The text that was posted
        """
        return self.request.form.get(('%stext' % self.input_prefix), u'')

    @property
    def post_tags(self):
        """ The tags that were added
        """
        return self.request.form.get('tags', [])

    @property
    def post_mentions(self):
        """ The mentions that were added
        """
        return self.request.form.get('mentions', [])

    @property
    @memoize
    def post_attachment(self):
        """
        The attachmented that was posted (if any)
        """
        return self.request.form.get(
            ('%sattachments' % self.input_prefix),
            None
        )

    @property
    def thread_id(self):
        """ Return the thread_id
        (used e.g. for commenting other status updates)
        """
        if 'thread_id' in self.request:
            return self.request.get('thread_id')
        if hasattr(self.context, 'thread_id') and self.context.thread_id:
            thread_id = self.context.thread_id  # threaded
        elif isinstance(self.context, StatusUpdate):
            thread_id = self.context.id  # first reply
        else:
            thread_id = None  # new
        return thread_id

    def userid2fullname(self, userid):
        """ Return the fullname for the post
        """
        try:
            fullname = api.user.get(userid).getProperty('fullname')
        except:
            fullname = ''
            msg = 'Problem getting fullname for userid "%s"' % userid
            logger.exception(msg)
        return fullname or userid

    def create_post_attachment(self, post):
        """ Check:
         - if the post supports attachments
         - if we have an attachment posted

        If both are True attach the data to the post
        """
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
        """ Return the post object or None

        To really proceed in the status update creation we require at least
        one of these two properties to evaluate to True
         - post_text
         - post_attachment

        If not of them evaluates to True we return None
        """
        if not (self.post_text or self.post_attachment):
            return
        post = piapi.microblog.statusupdate.create(
            text=self.post_text,
            microblog_context=self.post_context,
            thread_id=self.thread_id,
            mention_ids=self.post_mentions,
            tags=self.post_tags,
        )
        self.create_post_attachment(post)
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

    def get_post_as_comment(self, post):
        ''' Transforms a post (aka StatusUpdate) into a renderable comment
        '''
        return api.content.get_view(
            'statusupdate_view',
            post,
            self.request,
        ).as_comment

    def update(self):
        """ When updating we may want to process the form data and,
        if needed, create a post
        """
        self.activity_views = []
        if self.is_posting:
            self.post = self.create_post()
        else:
            self.post = None
        if self.post:
            self.activity_views.append(
                api.content.get_view(
                    'activity_view',
                    IStatusActivity(self.post),
                    self.request
                ).as_post
            )

    def __call__(self, *args, **kwargs):
        """ Call the multiadapter update

        We need to call the update manually (Tile instances don't do it)
        """
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
        if 'thread_id' in self.request.form:
            placeholder = _(
                u"leave_a_comment",
                default=u"Leave a comment..."
            )
        else:
            placeholder = _(
                u"add_statusupdate_button",
                default=u"What are you doing?"
            )
        return self.context.translate(placeholder)

    def get_pat_inject(self, form_id, thread_id):
        ''' This will return the a string to fill the
        data-pat-inject attribute

        It varies according to the fact we are creating:
         - a status update (no thread_id)
         - a comment to the status update
        '''
        if not thread_id:
            return (
                'source: #activity-stream; '
                'target: #activity-stream .activities::before && #%s'
            ) % form_id
        return (
            'source: #comment-trail-%(thread_id)s; '
            'target: #new-comment-%(thread_id)s ::element::before '
            '&& '
            'source: #microblog-%(thread_id)s; '
            'target: #microblog-%(thread_id)s; '
        ) % {
            'thread_id': thread_id,
        }
