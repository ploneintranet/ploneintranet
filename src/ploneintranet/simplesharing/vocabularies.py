from z3c.form.interfaces import NOT_CHANGED
from zope.interface import classProvides, implements
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from plone import api


WORKFLOW_MAPPING = {
    'private': 'draft',
    'limited': 'draft',
    'published': 'published',
    'public': 'public'
}


class WorkflowStatesSource(object):
    """
    A source that provides a list of workflow states for the current context
    """
    classProvides(IContextSourceBinder)
    implements(IContextSourceBinder)

    def _state_title_description(self, state):
        return u"%s (%s)" % (
            state.title,
            state.description,
        )

    def __call__(self, context):
        """get available workflows/transitions for this object

        :param context: the object being shared
        :returns: vocab of avaible states
        :rtype: SimpleVocabulary
        """
        workflow = api.portal.get_tool('portal_workflow')
        transitions = workflow.listActionInfos(object=context)
        workflows = workflow.getWorkflowsFor(context)
        states = workflows[0].states.objectValues()
        state_mapping = {x.id: x for x in states}
        current_state = api.content.get_state(obj=context)

        # add the current state
        vocab = [
            SimpleTerm(
                value=NOT_CHANGED,
                token=NOT_CHANGED,
                title=self._state_title_description(
                    state_mapping[current_state]),
            )
        ]
        final_states = []
        for transition in transitions:
            new_state = transition['transition'].new_state_id
            if new_state in final_states:
                continue
            transition_id = transition['transition'].id
            vocab.append(
                SimpleTerm(
                    value=transition_id,
                    token=transition_id,
                    title=self._state_title_description(
                        state_mapping[new_state]),
                )
            )
            final_states.append(new_state)

        return SimpleVocabulary(vocab)
