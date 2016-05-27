# coding=utf-8
import logging
from Products.CMFPlone.utils import safe_unicode
from Products.Five.browser import BrowserView
from plone import api
from plone.app.contenttypes.content import Image, File
from plone.memoize.view import memoize
from plone.memoize.view import memoize_contextless
from ploneintranet.attachments.utils import IAttachmentStorage
from ploneintranet.microblog.browser.utils import link_tags
from ploneintranet.microblog.browser.utils import link_users
from ploneintranet.microblog.browser.utils import link_urls
from ploneintranet import api as pi_api
from ploneintranet.core import ploneintranetCoreMessageFactory as _

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
        ''' Provide informations to display the avatar
        '''
        user = api.user.get(self.context.userid)

        if user:
            fullname = user.getProperty('fullname')
        else:
            fullname = userid

        url = u'%s/author/%s' % (
            self.portal_url,
            userid,
        )
        img = pi_api.userprofile.avatar_url(userid)
        avatar = {
            'id': userid,
            'fullname': fullname,
            'img': img,
            'url': url,
        }
        return avatar

    @property
    @memoize
    def avatar(self):
        ''' Provide informations to display the avatar
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
            item.getId(),
        ))
        is_image = False
        if isinstance(item, Image):
            is_image = True
            # # this suffers from a bug
            # # 'large' should return 768x768 but instead returns 400x400
            # images = api.content.get_view(
            #     'images',
            #     item.aq_base,
            #     self.request,
            # )
            # url = '/'.join((
            #     item_url,
            #     images.scale(scale='large').url.lstrip('/'),
            # ))
            # # use unscaled instead
            url = item_url
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

    @memoize
    def comment_views(self):
        ''' Return the way we can reply to this activity
        '''
        replies = list(self.context.replies())
        replies.reverse()
        replies_rendered = [
            api.content.get_view(
                'comment.html',
                reply,
                self.request)
            for reply in replies]
        return replies_rendered

    # ----------- actions (edit, delete) ----------------
    # actual write/delete handling done in subclass below

    @property
    def traverse(self):
        """Base URL for traversal views"""
        return "{}/statusupdate/{}".format(self.portal_url, self.context.id)

    @property
    def traverse_threadparent(self):
        """After editing a reply we need to show the full thread"""
        return "{}/statusupdate/{}".format(
            self.portal_url, self.context.thread_id)

    @property
    def actions(self):
        actions = []

        if self.context.can_delete:
            if self.context.thread_id:
                actions.append(dict(
                    icon='trash',
                    title='Delete comment',
                    url=self.traverse + '/panel-delete-comment.html'
                ))
            else:
                actions.append(dict(
                    icon='trash',
                    title='Delete post',
                    url=self.traverse + '/panel-delete-post.html'
                ))

        if self.context.can_edit:
            if self.context.thread_id:
                actions.append(dict(
                    icon='edit',
                    title='Edit comment',
                    url=self.traverse + '/panel-edit-comment.html'
                ))
            else:
                actions.append(dict(
                    icon='edit',
                    title='Edit post',
                    url=self.traverse + '/panel-edit-post.html'
                ))

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
        elif pi_api.previews.converting(self.content_context):
            return base + ' not-generated'
        elif not self.content_has_previews():
            return base + ' not-possible'
        else:
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
