# coding=utf-8
from plone.memoize.view import memoize
from ploneintranet.layout.browser.workflow import WorkflowMenu


class NewsWorkflowMenu(WorkflowMenu):
    ''' Customize the workflow menu for the news
    which have a separate edit view
    '''
    @property
    @memoize
    def injection_url(self):
        ''' The url to get this view
        '''
        return '/'.join((
            self.context.absolute_url(),
            'edit.html',
        ))
