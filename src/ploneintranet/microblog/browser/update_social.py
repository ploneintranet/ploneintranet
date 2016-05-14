# coding=utf-8
import logging
from Products.Five.browser import BrowserView
from plone import api

from datetime import datetime
from plone.memoize.view import memoize
from ploneintranet import api as piapi
from ploneintranet.attachments.attachments import IAttachmentStoragable
from ploneintranet.attachments.utils import extract_and_add_attachments
from ploneintranet.core import ploneintranetCoreMessageFactory as _
from ploneintranet.microblog.statusupdate import StatusUpdate

logger = logging.getLogger(__name__)


class UpdateSocialBase(BrowserView):
    """Shared base class for:
    - update-social.html
    - post-well-done.html
    - comment-well-said.html
    - panel-users
    """

    input_prefix = 'form.widgets.'
    button_prefix = 'form.buttons.'

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

    @property
    @memoize
    def is_posting(self):
        """ Check if the form was submitted
        """
        return ('%sstatusupdate' % self.button_prefix) in self.request.form

    @property
    @memoize
    def microblog_context(self):
        """ The context of this microblog post
        (the portal, a workspace, and so on...)
        """
        if isinstance(self.context, StatusUpdate):
            microblog_context = self.context.microblog_context
        else:
            microblog_context = piapi.microblog.get_microblog_context(
                self.context)
        if microblog_context:
            return microblog_context
        else:
            return api.portal.get()

    @property
    def microblog_context_url(self):
        return self.microblog_context.absolute_url()

    def portal_url(self):
        return api.portal.get().absolute_url()


class UpdateSocialHandler(UpdateSocialBase):
    """Shared HTTP POST handler for:
    - post-well-done.html
    - comment-well-said.html

    So excluding update-social.html.
    """

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
            microblog_context=self.microblog_context,
            thread_id=self.thread_id,
            mention_ids=self.post_mentions,
            tags=self.post_tags,
        )
        self.create_post_attachment(post)
        return post

    def update(self):
        """ When updating we may want to process the form data and,
        if needed, create a post
        """
        if self.is_posting:
            self.post = self.create_post()

    def __init__(self, *args, **kwargs):
        super(UpdateSocialHandler, self).__init__(*args, **kwargs)
        self.post = None

    def __call__(self, *args, **kwargs):
        """ Call the multiadapter update

        We need to call the update manually (Tile instances don't do it)
        """
        self.update()
        return super(UpdateSocialHandler, self).__call__(*args, **kwargs)


class UpdateSocialView(UpdateSocialBase):
    '''
    Show the form for creating a post or reply.
    Does not actually handle the HTTP POST.
    '''

    def form_action(self):
        if self.thread_id:
            _action = '%s/comment-well-said.html'
        else:
            _action = '%s/post-well-done.html'
        return _action % self.microblog_context_url

    @property
    def form_id(self):
        if self.thread_id:
            return 'comment_box_%s' % self.thread_id
        else:
            return 'post-box'

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
        return self.microblog_context.translate(placeholder)
