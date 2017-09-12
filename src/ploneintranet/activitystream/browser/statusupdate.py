# coding=utf-8
from plone import api
from plone.app.contenttypes.behaviors.leadimage import ILeadImage
from plone.app.contenttypes.content import File
from plone.app.contenttypes.content import Image
from plone.memoize.view import memoize
from plone.memoize.view import memoize_contextless
from ploneintranet import api as pi_api
from ploneintranet.activitystream.browser.utils import link_tags
from ploneintranet.activitystream.browser.utils import link_urls
from ploneintranet.activitystream.browser.utils import link_users
from ploneintranet.attachments.utils import IAttachmentStorage
from ploneintranet.core import ploneintranetCoreMessageFactory as _
from ploneintranet.layout.interfaces import IDiazoNoTemplate
from Products.CMFPlone.utils import safe_unicode
from Products.Five.browser import BrowserView
from zope.interface import implementer

import logging


logger = logging.getLogger('ploneintranet.activitystream')


class StatusUpdateView(BrowserView):
    ''' This view renders a status update

    See templates/post.html for an explanation of the various
    rendering modes.

    On top of that it also powers templates/comment.html

    The API could use some cleanup.
    '''

    newpostbox_placeholder = _(u'leave_a_comment',
                               default=u'Leave a comment...')

    @property
    @memoize_contextless
    def fresh_reply_limit(self):
        ''' How many replies are considered fresh?
        0 means "infinite"
        '''
        if not self.request.get('all_comments'):
            return 3
        else:
            return 0

    @property
    @memoize
    def commentable(self):
        '''
        Check whether the viewing user has the right to comment
        by resolving the containing workspace IMicroblogContext
        (falling back to None=ISiteRoot)
        '''
        add = 'Plone Social: Add Microblog Status Update'
        try:
            return api.user.has_permission(
                add,
                obj=self.context.microblog_context
            )
        except api.exc.UserNotFoundError:
            logger.error("UserNotFoundError while rendering a statusupdate.")
            return False

    @property
    @memoize
    def portal(self):
        ''' Return the portal object
        '''
        return api.portal.get()

    @property
    @memoize
    def portal_url(self):
        ''' Return the portal object url
        '''
        return self.portal.absolute_url()

    @property
    @memoize
    def context_url(self):
        ''' Return the context url
        '''
        return self.portal_url

    @property
    @memoize
    def toggle_like(self):
        ''' This is used to render the toggle like stuff
        '''
        toggle_like_base = api.content.get_view(
            'toggle_like_statusupdate',
            self.portal,
            self.request,
        )
        toggle_like_view = toggle_like_base.publishTraverse(
            self.request,
            self.context.getId(),
        )
        return toggle_like_view

    @property
    @memoize
    def decorated_text(self):
        ''' Use this method to enrich the status update text

        For example we can:
         - replace \n with <br />
         - add mentions
         - add tags
        '''
        text = safe_unicode(self.context.text).replace(u'\n', u'<br />')
        text = link_urls(text)
        tags = getattr(self.context, 'tags', None)
        mentions = getattr(self.context, 'mentions', None)
        text += link_users(self.portal_url, mentions)
        text += link_tags(self.portal_url, tags)
        return text

    @memoize_contextless
    def get_avatar_by_userid(self, userid):
        ''' Provide HTML tag to display the avatar
        '''
        return pi_api.userprofile.avatar_tag(
            username=userid,
        )

    @property
    def fullname(self):
        user = (
            pi_api.userprofile.get(self.context.userid) or
            api.user.get(self.context.userid)
        )
        fullname = ''
        if user:
            fullname = getattr(user, 'fullname', user.getProperty('fullname'))
        return fullname or self.context.userid

    @property
    @memoize
    def avatar(self):
        ''' Provide HTML tag to display the current user's avatar
        '''
        return self.get_avatar_by_userid(self.context.userid)

    @property
    @memoize
    def attachment_base_url(self):
        ''' This will return the base_url for making attachments
        '''
        base_url = '{portal_url}/@@status-attachments/{status_id}'.format(
            portal_url=self.portal_url,
            status_id=self.context.getId(),
        )
        return base_url

    def item2attachments(self, item):
        ''' Take the attachment storage item
        and transform it into an attachment
        '''
        item_url = '/'.join((
            self.attachment_base_url,
            safe_unicode(item.getId()),
        ))
        is_image = False
        if isinstance(item, Image):
            is_image = True
            # this suffers from a bug
            # 'large' should return 768x768 but instead returns 400x400
            images = api.content.get_view(
                'images',
                item.aq_base,
                self.request,
            )
            url = '/'.join((
                item_url,
                images.scale(scale='large').url.lstrip('/'),
            ))
        elif pi_api.previews.get(item):
            url = '/'.join((item_url, 'small'))
        else:
            url = None

        return {'is_image': is_image,
                'img_src': url,
                'link': item_url,
                'alt': item.id,
                'title': item.id}

    def attachments(self):
        """ Get preview images for status update attachments
        """
        storage = IAttachmentStorage(self.context, {})
        items = storage.values()
        return map(self.item2attachments, items)

    @property
    @memoize
    def replies(self):
        ''' Get the replies for this statusupdate
        '''
        replies = list(self.context.replies())
        replies.reverse()
        return replies

    @property
    def has_older_replies(self):
        ''' Check if we have oilder replies that we may want to hide
        '''
        if not self.fresh_reply_limit:
            return False
        return len(self.replies) > self.fresh_reply_limit

    @memoize
    def comment_views(self):
        ''' Return the html views of the replies to this comment
        '''
        replies_rendered = [
            api.content.get_view(
                'comment.html',
                reply,
                self.request
            )
            for reply in self.replies[-self.fresh_reply_limit:]
        ]
        return replies_rendered

    # ----------- actions (edit, delete) ----------------
    # actual write/delete handling done in subclass below

    @property
    def traverse(self):
        """Base URL for traversal views"""
        return "{}/statusupdate/{}".format(self.portal_url, self.context.id)

    @property
    def actions(self):
        actions = []
        if self.context.can_delete:
            if self.context.thread_id:
                title = _('Delete comment')
            else:
                title = _('Delete post')
            actions.append({
                'icon': 'trash',
                'title': title,
                'data_pat_modal': 'class: small',
                'url': self.traverse + '/panel-delete-post.html',
            })
        if self.context.can_edit:
            if self.context.thread_id:
                title = _('Edit comment')
            else:
                title = _('Edit post')
            actions.append({
                'icon': 'edit',
                'title': title,
                'url': self.traverse + '/panel-edit-post.html',
                'data_pat_modal': 'panel-header-content: none',
            })

        # edit_tags not implemented yet
        # edit_mentions not implemented yet
        return actions

    # ----------- content updates only ------------------

    @property
    @memoize
    def content_context(self):
        return self.context.content_context

    @property
    def is_content_update(self):
        return bool(self.content_context)

    @property
    def is_content_image_update(self):
        return (self.content_context and
                isinstance(self.content_context, Image))

    @property
    def is_content_file_update(self):
        return (self.content_context and
                isinstance(self.content_context, File))

    @property
    def is_content_downloadable(self):
        return (self.is_content_image_update or
                self.is_content_file_update)

    @property
    def content_has_leadimage(self):
        return (self.content_context and
                ILeadImage.providedBy(self.content_context))

    def content_has_previews(self):
        if not self.is_content_update:
            return False
        elif self.is_content_image_update:
            return True
        return pi_api.previews.has_previews(self.content_context)

    def content_preview_status_css(self):
        if not self.is_content_update:
            return 'fixme'
        base = 'document document-preview'
        if self.is_content_image_update:
            return base
        if pi_api.previews.converting(self.content_context):
            return base + ' not-generated'
        if not self.content_has_previews():
            return base + ' not-possible'
        return base

    def content_preview_urls(self):
        if not self.is_content_update:
            return []
        if self.is_content_image_update:
            return [self.content_context.absolute_url(), ]
        return pi_api.previews.get_preview_urls(
            self.content_context, scale='large')

    def content_url(self):
        if self.is_content_image_update or \
           self.is_content_file_update:
            return '{}/view'.format(self.content_context.absolute_url())
        elif self.is_content_update:
            return self.content_context.absolute_url()


@implementer(IDiazoNoTemplate)
class StatusUpdateEditPanel(StatusUpdateView):
    ''' Render the edit panel for posts or comments
    '''
    @property
    @memoize
    def title(self):
        if self.context.thread_id:
            return _('Edit comment')
        return _('Edit post')

    @property
    @memoize
    def form_action(self):
        if self.context.thread_id:
            return self.traverse + '/comment-edited.html'
        return self.traverse + '/post-edited.html'

    @property
    def selector_template(self):
        if self.context.thread_id:
            return '#{thread_id}-comment-{context_id} .comment-content'
        return '#post-{context_id} .post-content'

    @property
    @memoize
    def data_pat_inject(self):
        selector = self.selector_template.format(
            context_id=self.context.id,
            thread_id=self.context.thread_id,
        )
        return 'source: {selector}; target: {selector};'.format(
            selector=selector
        )


@implementer(IDiazoNoTemplate)
class StatusUpdateDeletePanel(StatusUpdateView):
    ''' Render the delete panel for posts or comments
    '''
    @property
    @memoize
    def title(self):
        if self.context.thread_id:
            return _('Delete comment')
        return _('Delete post')

    @property
    @memoize
    def description(self):
        if self.context.thread_id:
            return _('You are about to delete this comment. Are you sure?')
        return _('You are about to delete this post. Are you sure?')

    @property
    @memoize
    def form_action(self):
        if self.context.thread_id:
            return self.traverse + '/comment-deleted.html'
        return self.traverse + '/post-deleted.html'

    @property
    def selector_template(self):
        if self.context.thread_id:
            return '#{thread_id}-comment-{context_id}::element'
        return '#post-{context_id}::element'

    @property
    @memoize
    def data_pat_inject(self):
        selector = self.selector_template.format(
            context_id=self.context.id,
            thread_id=self.context.thread_id,
        )
        return 'source: #document-content; target: {selector};'.format(
            selector=selector
        )


class StatusUpdateModify(StatusUpdateView):
    """
    A shared view class for editing and deleting statusupdates.
    """

    def __call__(self):
        if self.request.method == 'POST':
            self.handle_action()
        return super(StatusUpdateModify, self).__call__()

    def handle_action(self):
        """
        Handle edit/delete actions. Security is checked in backend.
        Takes care to handle any HTTP POST only once, even with
        a cloned request.
        """
        # pop() removes id to avoid multi-handling cloned POST request
        id = self.request.form.pop('statusupdate_id', None)
        if not id:
            return
        statusupdate = pi_api.microblog.statusupdate.get(id)
        if self.request.form.get('delete', False):
            statusupdate.delete()
        elif self.request.form.get('text', None):
            statusupdate.edit(self.request.form.get('text'))
