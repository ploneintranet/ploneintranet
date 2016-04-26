# coding=utf-8
import logging
from DateTime import DateTime
from Products.CMFPlone.utils import safe_unicode
from Products.Five.browser import BrowserView
from plone import api
from plone.app.contenttypes.content import Image
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
    def toLocalizedTime(self):  # noqa
        ''' Facade for the toLocalizedTime method
        '''
        return api.portal.get_tool('translation_service').toLocalizedTime

    @property
    @memoize
    def date(self):
        ''' The date of our context object
        '''
        # We have to transform Python datetime into Zope DateTime
        # before we can call toLocalizedTime.
        date = self.raw_date

        return self.toLocalizedTime(
            date,
            long_format=True,
        )

    @property
    @memoize
    def raw_date(self):
        ''' The raw date of our context object
        '''
        date = self.context.date
        if hasattr(date, 'isoformat'):
            date = DateTime(self.context.raw_date.isoformat())
        return date

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

    @property
#    @memoize
    def content_context(self):
        return self.context.content_context

    @property
    def is_content_update(self):
        return bool(self.content_context)

    @property
    def is_content_image_update(self):
        return isinstance(self.content_context, Image)

    @property
    def is_content_downloadable(self):
        return self.is_content_image_update  # FIXME: support File

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
        if self.is_content_image_update:  # FIXME: or File
            return '{}/view'.format(self.content_context.absolute_url())
        elif self.is_content_update:
            return self.content_context.absolute_url()
