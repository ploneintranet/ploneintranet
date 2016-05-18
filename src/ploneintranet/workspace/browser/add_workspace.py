from collections import defaultdict
from datetime import datetime
from plone import api
from plone.memoize.view import memoize
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.schema.interfaces import IVocabularyFactory
from zope.component import getUtility

from ploneintranet.core import ploneintranetCoreMessageFactory as _  # noqa
from ploneintranet.workspace.config import TEMPLATES_FOLDER
from ploneintranet.workspace.browser.add_content import AddBase
from ploneintranet.workspace.unrestricted import execute_as_manager

vocab = 'ploneintranet.workspace.vocabularies.Divisions'


class AddWorkspace(AddBase):
    """
    Evaluate simple form and add arbitrary content.
    """

    template = ViewPageTemplateFile('templates/add_workspace.pt')

    TEMPLATES_FOLDER = TEMPLATES_FOLDER
    default_fti = 'ploneintranet.workspace.workspacefolder'

    # BBB: this hardcoded class attributes should be dynamic properties
    # I see two possible way:
    # 1. Generic setup: store the information in the portal_type definition xml
    # 2. Portal_registry: add two properties
    # If it is easy I would go for 1.
    types_with_template = (
        'ploneintranet.workspace.case',
        'ploneintranet.workspace.workspacefolder',
    )
    types_with_policy = (
        'ploneintranet.workspace.workspacefolder',
    )

    def get_template(self):
        ''' Get a template to copy
        '''
        with api.env.adopt_roles('Manager'):
            template_id = self.request.form.get(
                '%s-template_id' % self.portal_type
            )
            if not template_id:
                return
            portal = api.portal.get()
            template_folder = portal.get(self.TEMPLATES_FOLDER)
            if not template_folder:
                return
            src = template_folder.get(template_id)
            if not src:
                return
            return src

    def create_from_template(self):
        ''' Create an ocject with the given template
        '''
        template = self.get_template()
        if not template:
            api.portal.show_message(
                _('Please specify which Case Template to use'),
                request=self.request,
                type="error",
            )
            return

        # need privilege escalation since normal users do not
        # have View permission on case templates
        # - that only comes after the template has been turned
        # into an actual case with member users
        new = execute_as_manager(
            api.content.copy,
            source=template,
            target=self.context,
            id=self.get_new_unique_id(),
            safe_id=False,
        )
        new.creation_date = datetime.now()
        return new

    def get_new_object(self):
        ''' This will create a new object
        '''
        if (
            self.portal_type in self.types_with_template and
            self.request.form.get('%s-template_id' % self.portal_type)
        ):
            return self.create_from_template()
        return super(AddWorkspace, self).get_new_object()

    def set_workspace_policy(self, obj):
        ''' Set's the workspace policy for the objects given a scenario
        '''
        form = self.request.form
        if 'scenario' in form:
            if form['scenario'] == '1':
                external_visibility = 'secret'
                join_policy = 'admin'
                participant_policy = 'producers'
            elif form['scenario'] == '2':
                external_visibility = 'private'
                join_policy = 'team'
                participant_policy = 'moderators'
            elif form['scenario'] == '3':
                external_visibility = 'open'
                join_policy = 'self'
                participant_policy = 'publishers'
            else:
                raise AttributeError

            obj.set_external_visibility(external_visibility)
            obj.join_policy = join_policy
            obj.participant_policy = participant_policy

    def update(self, obj):
        ''' Update the object and returns the modified fields and errors
        '''
        if self.portal_type in self.types_with_policy:
            self.set_workspace_policy(obj)
        return super(AddWorkspace, self).update(obj)

    @memoize
    def get_addable_types(self):
        ''' List the content that are addable in this context
        '''
        ftis = self.context.allowedContentTypes()
        selected_fti = self.request.get(
            'portal_type',
            self.default_fti
        )
        addable_types = [
            {
                'id': fti.getId(),
                'title': fti.Title(),
                'selected': fti.getId() == selected_fti and 'selected' or None,
            }
            for fti in ftis
        ]
        addable_types.sort(key=lambda x: x['title'])
        return addable_types

    @memoize
    def get_fti_titles_by_type(self):
        ''' Get's the titles of the fti by portal_type as a dictionary
        '''
        return {
            x['id']: x['title']
            for x in self.get_addable_types()
        }

    @memoize
    def get_templates_by_type(self):
        ''' Get's the templates as a dictionary
        to fill a select or a radio group
        '''
        portal = api.portal.get()
        templates_folder = portal.get(self.TEMPLATES_FOLDER)
        allowed_types = {x['id'] for x in self.get_addable_types()}
        templates_by_type = defaultdict(list)
        for template in templates_folder.objectValues():
            if template.portal_type in allowed_types:
                templates_by_type[template.portal_type].append(
                    {
                        'id': template.getId(),
                        'title': template.Title(),
                        'portal_type': template.portal_type,
                        'description': template.Description(),
                    }
                )
        for key in templates_by_type:
            templates_by_type[key].sort(key=lambda x: x['title'])
        return templates_by_type

    def divisions(self):
        divisions = getUtility(IVocabularyFactory, vocab)(self.context)
        return divisions
