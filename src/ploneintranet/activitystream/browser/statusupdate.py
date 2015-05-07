# coding=utf-8
from DateTime import DateTime
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone import api
from plone.app.contenttypes.content import Image
from plone.memoize.view import memoize
from ploneintranet.attachments.utils import IAttachmentStorage
from ploneintranet.docconv.client.interfaces import IDocconv
<<<<<<< HEAD
=======
from zope.component import getMultiAdapter
>>>>>>> Added status update view


class StatusUpdateView(BrowserView):
    ''' This view renders a status update
    '''
<<<<<<< HEAD
<<<<<<< HEAD
    as_comment = ViewPageTemplateFile('templates/statusupdate_as_comment.pt')

    commentable = True
=======

    as_reply = ViewPageTemplateFile('templates/statusupdate_as_reply.pt')
>>>>>>> Added status update view
=======
    as_comment = ViewPageTemplateFile('templates/statusupdate_as_comment.pt')

    commentable = True
>>>>>>> Replace reply_providers with views on status updates

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
        time = self.context.raw_date
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
    def attachment_base_url(self):
        ''' This will return the base_url for making attachments
        '''
        portal_url = api.portal.get().absolute_url()
        base_url = '{portal_url}/@@status-attachments/{status_id}'.format(
            portal_url=portal_url,
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

<<<<<<< HEAD
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
=======
    def statusreply_provider(self):
        raise Exception('Ciao')
        # if not self.highlight():
        #     return
        provider = getMultiAdapter(
            (self.status, self.request, self),
            name="ploneintranet.microblog.statusreply_provider"
        )
        provider.update()
        return provider()

    @memoize
    def comment_views(self):
        ''' Return the way we can reply to this activity
        '''
<<<<<<< HEAD
        name = (
            "ploneintranet.activitystream.statusactivityinlinereply_provider"
        )
        for reply in self.context.replies():
            provider = getMultiAdapter(
                (reply, self.request, self),
                name=name
            )
            provider.update()
            yield provider
>>>>>>> Added status update view
=======
        return [
            api.content.get_view(
                'statusupdate_view',
                reply,
                self.request,
            ).as_comment for reply in self.context.replies()
        ]
>>>>>>> Replace reply_providers with views on status updates
