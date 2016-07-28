# coding=utf-8
from plone import api
from ploneintranet.core import ploneintranetCoreMessageFactory as _
from ploneintranet.workspace.basecontent.baseviews import ContentView
from ploneintranet.workspace.basecontent.utils import get_selection_classes


class EventView(ContentView):
    ''' This view specializes the content view for events
    '''

    def validate(self):
        ''' Override base content validation

        Return truish if valid
        '''
        if self.request.get('start') <= self.request.get('end'):
            return True

        api.portal.show_message(
            _('Start date should be lower than end date'),
            request=self.request,
            type="error"
        )
        return False

    def get_selection_classes(self, field, default=None):
        """ identify all groups in the invitees """
        return get_selection_classes(self.context, field, default)
