# -*- coding: utf-8 -*-
from plone import api

import re


TAGRE = re.compile('(#(\S+))')
USERRE = re.compile('(@\S+)')


def link_tags(text, url=''):
    tmpl = '<a href="%s/@@stream/tag/\\2" class="tag tag-\\2">\\1</a>'
    return TAGRE.sub(tmpl % url, text)


def link_users(text, url=''):
    user_tmpl = '<a href="{0}/@@author/{1}" class="user user-{1}">@{2}</a>'
    user_marks = USERRE.findall(text)
    for user_mark in user_marks:
        user_id = user_mark[1:]
        user = api.user.get(username=user_id)
        if user:
            user_fullname = user.getProperty('fullname', '') or user_id
            text = re.sub(
                user_mark,
                user_tmpl.format(
                    url,
                    user_id,
                    user_fullname),
                text
            )
    return text
