from plone import api


def set_show_extra_cookie(request, section):
    """Users can show only "my documents" or include archived documents
       or archived tags.  Archived items are then hidden from
       view. They can however choose to show these archives.

       The choice whether archived elements must be shown is stored in
       a cookie as string of pipe-separated ("|") values.

       For example: 'documents|tags' or 'documents' or 'tags'
    """
    cookie_name = '%s-show-extra-%s' % (
        section, api.user.get_current().getId())
    values = request.get(cookie_name, '').split('|')
    for t in ['archived_documents', 'archived_tags', 'my_documents']:
        if request.form.get('show_%s' % t):
            if t not in values:
                values.append(t)
        elif request.form.get('show_%s-empty-marker' % t):
            if t in values:
                values.remove(t)
    cookie_value = '|'.join(values)
    request.set(cookie_name, cookie_value)
    request.response.setCookie(cookie_name, cookie_value)
