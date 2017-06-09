# coding=utf-8
from plone import api
from plone.memoize.view import memoize
from ploneintranet.core import ploneintranetCoreMessageFactory as _
from ploneintranet.workspace.basecontent.baseviews import ContentView
from ploneintranet.workspace.basecontent.utils import get_selection_classes
from re import compile


uid_pattern = compile('([0-9a-f]){32}')


class EventView(ContentView):
    ''' This view specializes the content view for events
    '''
    def form_pat_inject_options(self):
        ''' Return the data-path-inject options we want to use
        '''
        parts = [
            'source: #{mainid}; target: #{mainid};',
            "source: #workspace-events; target: #workspace-events; loading-class: ''",  # noqa
        ]
        if self.autosave_enabled:
            mainid = 'saving-badge'
        else:
            mainid = 'document-body'
            parts.append(
                '#global-statusmessage; target:#global-statusmessage; '
                'loading-class: \'\''
            )
        template = ' && '.join(parts)
        return template.format(
            mainid=mainid,
        )

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

    @memoize
    def get_agenda_items(self):
        ''' Return the agenda items to create the agenda_items widget

        An agenda item may be a simple string or an assigned uid.

        We return a list dict like:
        {
            'brain': brain or None,
            'read_only': boolean,
            'value': unicode,
            'url': unicode,

        }

        Each dict "value" will be the items in the agenda_items field list.
        Each dict "brain" will be the brain relative to the given value,
        or None if value does not resolve into a brain
        Each dict will be set as read_only if it looks like a uid or
        if the user has no edit rights on the document.

        '''
        values = filter(None, self.context.agenda_items)
        if not values:
            return []

        can_edit = self.can_edit
        pc = api.portal.get_tool('portal_catalog')
        brains = pc.unrestrictedSearchResults(UID=values)
        mapping = {brain.UID: brain for brain in brains}
        return [
            {
                'read_only': (not can_edit) or (value in mapping),
                'brain': mapping.get(value, None),
                'value': value,
            }
            for value in values
            if value in mapping or not uid_pattern.match(value)
        ]

    def get_agenda_item_badges(self, item):
        ''' Given an item returned by self.get_agenda_items,
        return a list of badges. A badge will be modeled in to a dict like:
        {
            'klass': 'css class',
            'label': 'some text',
        }
        '''
        return []
