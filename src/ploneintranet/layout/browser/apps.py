from zope.publisher.browser import BrowserView
from ploneintranet.core import ploneintranetCoreMessageFactory as _  # noqa
from plone import api


class AppNotAvailable(BrowserView):

    """ A nice not available page to be able to demo this beautifully
    """


class Apps(BrowserView):

    """ A view to serve as overview over apps
    """

    def tiles(self):
        """
        list available tiles
        This has currently mostly teaser function
        later this will query a registry to list all tiles registered in the
        system.
        """
        portal_url = api.portal.get().absolute_url()
        imgtpl = '{0}/++theme++ploneintranet.theme/generated/apps/{1}/icon.svg'

        def _gen_tile(id,
                      title,
                      disabled='disabled',
                      url=None,
                      modal='pat-modal'):
            if not url:
                url = '{0}/app-not-available.html#document-content' \
                      .format(portal_url)
            else:
                url = '{0}/{1}'.format(portal_url, url)
            tile = dict(title=_(title),
                        url=url,
                        cls='app-{0}'.format(id),
                        disabled=disabled,
                        modal=modal,
                        img=imgtpl.format(portal_url, id),
                        alt=_(u'{0} Application'.format(title)))
            return tile

        tiles = [
            _gen_tile('contacts', u'Contacts'),
            _gen_tile('messages', u'Messages'),
            _gen_tile('todo', u'Todo'),
            _gen_tile('calendar', u'Calendar'),
            _gen_tile('slide-bank', u'Slide bank'),
            _gen_tile('image-bank', u'Image bank'),
            _gen_tile('news', u'News publisher'),
            # _gen_tile('case-manager',
            #           u'Case manager',
            #           disabled='',
            #           url='@@case-manager',
            #           modal=''),
            _gen_tile('case-manager', u'Case manager',),
            _gen_tile('app-market', u'App market'),
        ]

        return tiles
