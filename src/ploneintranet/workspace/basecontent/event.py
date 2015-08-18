# coding=utf-8
from ploneintranet.workspace.basecontent.baseviews import ContentView
from urllib import urlencode


class EventView(ContentView):
    ''' This view specializes the content view for events
    '''
    def delete_url(self):
        ''' Prepare a url to the delete form triggering:
         - pat-modal
         - pat-inject
        '''
        options = {
            'pat-modal': 'true',
            'pat-inject': ' && '.join([
                'source:#document-body; target:#document-body',
                'source:#workspace-events; target:#workspace-events',
                'target:#global-statusmessage; source:#global-statusmessage',
            ])
        }
        return "%s/delete_confirmation?%s#content" % (
            self.context.absolute_url(),
            urlencode(options)
        )
