from plone import api
from plone.dexterity.content import Item
from plone.supermodel import model
from ploneintranet.workspace.adapters import IMetroMap
from ploneintranet.workspace.case import ICase
from ploneintranet.workspace.utils import parent_workspace
from zope.interface import implements

from ..behaviors import ITodoMarker


class ITodo(model.Schema):
    """A todo content type
    """


class Todo(Item):
    implements(ITodo, ITodoMarker)

    def reopen(self):
        """
        This only applies to Todo items in Case Workspaces.

        Set the workflow state to "open" if the milestone of the Todo item is
        the same as the current, or earlier workflow state of the Case
        Workspace, otherwise set to "planned".

        Only Open items will appear in the dashboard.
        """
        todo_state = api.content.get_state(self)
        workspace = parent_workspace(self)
        if not ICase.providedBy(workspace):
            if todo_state != 'open':
                api.content.transition(self, 'set_to_open')
        else:
            milestone = self.milestone
            if milestone:
                case_state = api.content.get_state(workspace)
                mm = IMetroMap(workspace).metromap_sequence.keys()
                future = mm.index(milestone) > mm.index(case_state)
                current_or_past = not future
                if current_or_past and todo_state != 'open':
                    api.content.transition(self, 'set_to_open')
                if future and todo_state != 'planned':
                    api.content.transition(self, 'set_to_planned')
            elif todo_state != 'planned':
                api.content.transition(self, 'set_to_planned')

    def set_appropriate_state(self):
        """
        If a Todo item is 'done', leave it, otherwise set it to 'open' or
        'planned' as appropriate.
        """
        state = api.content.get_state(self)
        if state == 'done':
            return
        else:
            self.reopen()
