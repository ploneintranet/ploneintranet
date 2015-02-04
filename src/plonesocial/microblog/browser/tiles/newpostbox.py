# -*- coding: utf-8 -*-
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.tiles import Tile
from zope.component import getMultiAdapter


class NewPostBoxTile(Tile):

    index = ViewPageTemplateFile('templates/new-post-box-tile.pt')
    is_attachment_supported = True

    def __call__(self, *args, **kwargs):
        ''' Call the multiadapter update

        #BBB this is an intermediate step

        After this step we will move the logic to this view
        '''
        provider = getMultiAdapter(
            (self.context, self.request, self),
            name='plonesocial.microblog.status_provider'
        )
        provider.update()
        token = provider.form.attachment_form_token()
        self.form = {'attachment_form_token': token}
        return super(NewPostBoxTile, self).__call__(*args, **kwargs)
