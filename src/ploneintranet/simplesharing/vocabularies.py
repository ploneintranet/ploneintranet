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

    def __call__(self, context):
        workflow = api.portal.get_tool('portal_workflow')
        wf = workflow.getWorkflowsFor(context)
        if not wf:
            return SimpleVocabulary([])
        states = wf[0].states.objectValues()
        return SimpleVocabulary([
            SimpleTerm(value=x.id,
                       token=x.id,
                       title=x.description) for x in states
        ])
