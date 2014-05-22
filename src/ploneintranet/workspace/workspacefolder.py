from five import grok

from plone import api
from plone.dexterity.content import Container
from plone.directives import form
from plone.namedfile.interfaces import IImageScaleTraversable


class IWorkspaceFolder(form.Schema, IImageScaleTraversable):
    """
    Interface for WorkspaceFolder
    """


class WorkspaceFolder(Container):
    """
    A WorkspaceFolder users can collaborate in
    """
    grok.implements(IWorkspaceFolder)

    # Block local role acquisition so that users
    # must be given explicit access to the workspace
    __ac_local_roles_block__ = 1

    def acquire_workspace(self):
        """
        helper method to acquire the workspace
        :rtype: ploneintranet.workspace.workspace
        """
        return self

    @property
    def external_visibility(self):
        return api.content.get_state(self)

    @external_visibility.setter
    def external_visibility(self, value):
        api.content.transition(obj=self, to_state=value)

    @property
    def join_policy(self):
        try:
            return self._join_policy
        except AttributeError:
            return "admin"

    @join_policy.setter
    def join_policy(self, value):
        self._join_policy = value

    @property
    def participant_policy(self):
        try:
            return self._participant_policy
        except AttributeError:
            return "Consumers"

    @participant_policy.setter
    def participant_policy(self, value):
        self._participant_policy = value
