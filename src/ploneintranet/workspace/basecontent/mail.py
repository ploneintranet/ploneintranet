# coding=utf-8
from ploneintranet.workspace.basecontent.baseviews import ContentView


class MailView(ContentView):
    ''' This view specializes the content view for  the
    ``ploneintranet.workspace.mail`` content type
    '''
    _edit_permission = 'Manage portal content'
    sidebar_target = 'workspace-documents'
