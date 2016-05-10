# coding=utf-8
from plone import api
from ploneintranet.core import ploneintranetCoreMessageFactory as _


class BaseTile(object):
    key = ''
    title = ''
    disabled = 'disabled'
    modal = 'pat-modal'
    path = ''
    position = 0

    _alt_template = u'{0} Application'
    _cls_template = 'app-{0}'
    _image_template = '{0}/++theme++ploneintranet.theme/generated/apps/{1}/icon.svg'  # noqa
    _url_not_available_template = '{0}/app-not-available.html#document-content'

    def __init__(self, context):
        ''' Add the context to this tile
        '''
        self.context = context

    @property
    def sorting_key(self):
        ''' We want to sort the tile according to position and title
        '''
        return (self.position, self.title)

    @property
    def cls(self):
        ''' Return the alt text for the image
        '''
        return self._cls_template.format(self.key)

    @property
    def alt(self):
        ''' Return the alt text for the image
        '''
        portal_url = api.portal.get().absolute_url()
        return self._alt_template.format(portal_url, self.title)

    @property
    def img(self):
        ''' Return the img src generated from the template
        '''
        portal_url = api.portal.get().absolute_url()
        return self._image_template.format(portal_url, self.key)

    @property
    def url(self):
        ''' Return the url generated from the path
        '''
        portal_url = api.portal.get().absolute_url()
        if not self.path:
            url = self._url_not_available_template.format(
                portal_url
            )
        else:
            url = '{0}/{1}'.format(
                portal_url,
                self.path,
            )
        return url


class ContactsTile(BaseTile):
    key = 'contacts'
    title = _('contacts', 'Contacts')
    position = 10


class MessagesTile(BaseTile):
    key = 'messages'
    title = _('messages', 'Messages')
    position = 20


class TodoTile(BaseTile):
    key = 'todo'
    title = _('todo', 'Todo')
    position = 30


class CalendarTile(BaseTile):
    key = 'calendar'
    title = _('calendar', 'Calendar')
    position = 40


class SlideBankTile(BaseTile):
    key = 'slide-bank'
    title = _('slide-bank', u'Slide bank')
    position = 50


class ImageBankTile(BaseTile):
    key = 'image-bank'
    title = _('image-bank', u'Image bank')
    position = 60


class NewsTile(BaseTile):
    key = 'news'
    title = _('news', u'News publisher')
    position = 70


class CaseManagerTile(BaseTile):
    key = 'case-manager'
    title = _('case-manager', u'Case manager',)
    position = 80


class AppMarketTile(BaseTile):
    key = 'app-market'
    title = _('app-market', u'App market')
    position = 90
