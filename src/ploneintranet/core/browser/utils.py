# -*- coding: utf-8 -*-


def link_tags(url='', tags=None):
    if tags:
        tmpl = u' <a href="%s/@@stream/tag/%s" class="tag tag-%s">#%s</a>'
        text = u' &mdash;'
        for tag in tags:
            text += tmpl % (url, tag, tag, tag)
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
