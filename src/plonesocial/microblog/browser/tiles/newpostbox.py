# -*- coding: utf-8 -*-
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.memoize.view import memoize
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
        return u"What are you doing?"
