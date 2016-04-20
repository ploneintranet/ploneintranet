# -*- coding: utf-8 -*-
from ttp import ttp
from Products.CMFPlone.utils import safe_unicode


def link_tags(url='', tags=None):
    if tags:
        # This is outcommented only temporarily to get Venus out. Refs
        # https://github.com/ploneintranet/ploneintranet/issues/426
        # tmpl = (u' <a href="{url}/@@stream/tag/{tag}" class="tag tag-{tag}">'
        #         u'#{tag}</a>')
        tmpl = (u' <span class="tag tag-{tag}">'
                u'#{tag}</span>')
        text = u' &mdash;'
        for tag in tags:
            text += tmpl.format(url=url, tag=safe_unicode(tag))
        return text
    return u''


def link_users(url='', mentions=None):
    if mentions:
        tmpl = u' <a href="{0}/@@author/{1}" class="user user-{1}">@{2}</a>'
        text = u' &mdash;'
        for user_id, fullname in mentions.items():
            if not isinstance(fullname, unicode):
                fullname = fullname.decode('utf8')
            text += tmpl.format(url, user_id, fullname)
        return text
    return u''


def link_urls(text):
    """
    Enriches urls in the comment text with an anchor.
    """
    parser = ttp.Parser(max_url_length=40)
    parser._urls = []
    return ttp.URL_REGEX.sub(parser._parse_urls, text)
