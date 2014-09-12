# -*- coding: utf-8 -*-
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone import api
from plonesocial.core.integration import PLONESOCIAL


class Tags(BrowserView):

    index = ViewPageTemplateFile('panel_tags.pt')

    def tags(self):
        """ Get available tags, both from Plone's keyword index
            and the microblog utility

        Applies very basic text searching
        """
        catalog = api.portal.get_tool('portal_catalog')
        tags = set(catalog.uniqueValuesFor('Subject'))

        # TODO: Check if the user is actually allowed to view these tags
        tool = PLONESOCIAL.microblog
        if tool:
            tags.update(tool._tag_mapping.keys())

        tags = sorted(tags)

        search_string = self.request.form.get('tagsearch')
        if search_string:
            search_string = search_string.lower()
            tags = filter(lambda x: search_string in x.lower(),
                          tags)
            if search_string not in tags:
                # add searched string as first item in list
                # if it doesn't exist
                tags = [search_string] + tags

        return tags
