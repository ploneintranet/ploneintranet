# coding=utf-8
from DateTime import DateTime
from Products.CMFPlone.utils import safe_unicode
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone import api
from plone.app.contenttypes.content import Image
from plone.memoize.view import memoize
from plone.memoize.view import memoize_contextless
from ploneintranet.attachments.utils import IAttachmentStorage
from ploneintranet.core.browser.utils import link_tags
from ploneintranet.core.browser.utils import link_users
from ploneintranet.docconv.client.interfaces import IDocconv


class StatusUpdateView(BrowserView):
    ''' This view renders a status update
    '''
    as_comment = ViewPageTemplateFile('templates/statusupdate_as_comment.pt')
    post_avatar = ViewPageTemplateFile('templates/statusupdate_post_avatar.pt')
    comment_avatar = ViewPageTemplateFile('templates/statusupdate_comment_avatar.pt')  # noqa
    commentable = True

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
            'toggle_like',
            self.portal,
            self.request,
        )
        toggle_like_view = toggle_like_base.publishTraverse(
            self.request,
            self.context.getId,
        )
        return toggle_like_view

    @property
    @memoize
    def newpostbox_view(self):
        ''' Return the newpostbox.tile view
        '''
        return api.content.get_view(
            'newpostbox.tile',
            self.portal,
            self.request,
        )

    @property
    @memoize
    def toLocalizedTime(self):
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
        time = self.context.date
        if hasattr(time, 'isoformat'):
            time = DateTime(self.context.raw_date.isoformat())

        if DateTime().Date() == time.Date():
            time_only = True
        else:
            # time_only=False still returns time only
            time_only = None

        return self.toLocalizedTime(
            time,
            long_format=True,
            time_only=time_only
        )

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
        tags = getattr(self.context, 'tags', None)
        mentions = getattr(self.context, 'mentions', None)
        text += link_users(self.portal_url, mentions)
        text += link_tags(self.portal_url, tags)
        return text

    @memoize_contextless
    def get_avatar_by_userid(
        self, userid, show_link=False, css='', attributes={}
    ):
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
        img = u'%s/portal_memberdata/portraits/%s' % (
            self.portal_url,
            userid,
        )
        avatar = {
            'id': userid,
            'fullname': fullname,
            'img': img,
            'url': url,
            'show_link': show_link,
            'css': css,
            'attributes': attributes,
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
        ''' Take the attachment sotrage item
        and transform it into an attachment
        '''
        docconv = IDocconv(item)
        item_url = '/'.join((
            self.attachment_base_url,
            item.getId(),
        ))
        if docconv.has_thumbs():
            url = '/'.join((item_url, 'thumb'))
        elif isinstance(item, Image):
            images = api.content.get_view(
                'images',
                item.aq_base,
                self.request,
            )
            url = '/'.join((
                item_url,
                images.scale(scale='preview').url.lstrip('/'),
            ))
        else:
            # We need a better fallback image. See #122
            url = '/'.join((
                api.portal.get().absolute_url(),
                '++theme++ploneintranet.theme/generated/media/logo.svg'
            ))
        return {'img_src': url, 'link': item_url}

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
        return [
            api.content.get_view(
                'statusupdate_view',
                reply,
                self.request,
            ).as_comment for reply in self.context.replies()
        ]
