# -*- coding: utf-8 -*-
import re
from Products.CMFPlone.utils import safe_unicode


def link_tags(url='', tags=None):
    if tags:
        tmpl = (u' <a href="{url}/@@stream/tag/{tag}" class="tag tag-{tag}">'
                u'#{tag}</a>')
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
    urlfinder = re.compile('(http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+)')  # noqa
    return urlfinder.sub(r'<a href="\1" target="_blank">\1</a>', text)
