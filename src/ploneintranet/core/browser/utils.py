# -*- coding: utf-8 -*-
from Products.CMFPlone.utils import safe_unicode
from plone import api

import re


TAGRE = re.compile('(#(\S+))')
USERRE = re.compile('(@\S+)')


def link_tags(url='', tags=None):
    if tags:
        tmpl = u' <a href="{url}/@@stream/tag/{tag}" class="tag tag-{tag}">#{tag}</a>'
        text = u' &mdash;'
        for tag in tags:
            text += tmpl.format(url=url, tag=safe_unicode(tag))
        return text
    return ''


def link_users(text, url=''):
    user_tmpl = u'<a href="{0}/@@author/{1}" class="user user-{1}">@{2}</a>'
    user_marks = USERRE.findall(text)
    for user_mark in user_marks:
        user_id = user_mark[1:]
        user = api.user.get(username=user_id)
        if user:
            user_fullname = user.getProperty('fullname', '') or user_id
            if not isinstance(user_fullname, unicode):
                user_fullname = user_fullname.decode('utf8')
            text = re.sub(
                user_mark,
                user_tmpl.format(
                    url,
                    user_id,
                    user_fullname),
                text
            )
    return text
