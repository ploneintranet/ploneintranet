from collections import defaultdict
from datetime import datetime
from plone import api
from plone.memoize.view import memoize
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.schema.interfaces import IVocabularyFactory
from zope.component import getUtility

from ploneintranet.core import ploneintranetCoreMessageFactory as _
from ploneintranet.workspace.config import TEMPLATES_FOLDER
from ploneintranet.workspace.browser.add_content import AddBase
from ploneintranet.workspace.utils import purge_and_refresh_security_manager

vocab = 'ploneintranet.workspace.vocabularies.Divisions'


class AddWorkspace(AddBase):
    """
    Adds a workspace-ish. Supports multiple variants:
    1. policy 'packages' on the default workspacefolder
       (hardcoded)
    2. templates on any variant of workspace-ish
       (discovered from templates folder)
    3. any workspace-ish without a template
       (discovered from addable types)

    Templates are security filtered: you can only use a template if
    you have access to the template, typically because you're a member
    of the template, possibly via an indirect group membership.
    """

    template = ViewPageTemplateFile('templates/add_workspace.pt')

    TEMPLATES_FOLDER = TEMPLATES_FOLDER
    default_fti = 'ploneintranet.workspace.workspacefolder'

    # policies are hardcoded in the template as well
    policies = dict(secret=dict(join_policy='admin',
                                participant_policy='producers'),
                    private=dict(join_policy='team',
                                 participant_policy='moderators'),
                    open=dict(join_policy='self',
                              participant_policy='publishers'),)

    # rendering helpers

    def workspace_templates(self):
        """Templates for normal workspaces"""
        return self.templates_by_type(self.default_fti)

    def special_options(self):
        """All the template options for non-default workspace types.
        Plus: an option for each type without a template"""
        options = []
        # templates
        for (typ, templates) in self.templates_by_type().items():
            if typ == self.default_fti:
                continue  # already in workspace_options
            options.extend(templates)
        options.extend(self.special_templateless())
        return options

    def special_templateless(self):
        "addable but no template and not a default workspace"
        alreadyhave = self.templates_by_type().keys()
        alreadyhave.append(self.default_fti)
        return [dict(id=typ, title=typ, portal_type=typ)
                for typ in self._addable_types()
                if typ not in alreadyhave]

    def all_templates(self):
        return self.workspace_templates() + self.special_options()

    @property
    def all_templates_dict(self):
        return {template['id']: template
                for template in self.all_templates()
                if template not in self.special_templateless()}

    def _addable_types(self):
        return [fti.getId() for fti in self.context.allowedContentTypes()]

    @memoize
    def templates_by_type(self, typ=None):
        ''' Get's the templates as a dictionary
        to fill a select or a radio group
        '''
        allowed_types = self._addable_types()
        templates_by_type = defaultdict(list)
        for template in self.allowed_templates.values():
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
        if typ:
            if typ in templates_by_type:
                return templates_by_type[typ]
            else:
                return []
        return templates_by_type

    @property
    def allowed_templates(self):
        return self._allowed_templates()

    @memoize
    def _allowed_templates(self):
        """A {id: template} dict containing only the templates
        which are accessible for the current user.
        """
        portal = api.portal.get()
        templates_folder = portal.get(self.TEMPLATES_FOLDER)
        if not templates_folder:
            return {}
        return {brain.getId: brain.getObject()
                for brain in templates_folder.getFolderContents()
                if brain.getId not in self.policies}

    def divisions(self):
        divisions = getUtility(IVocabularyFactory, vocab)(self.context)
        return divisions

    # POST handler

    def __call__(self):
        """Render form, or handle POST and redirect"""
        title = self.request.form.get('title', None)
        selected = self.request.form.get('workspace-type', None)
        if not (title and selected):
            return self.template()

        if selected in self.policies:
            self.portal_type = self.default_fti
        elif selected in self.all_templates_dict:
            templates = self.all_templates_dict
            self.portal_type = templates[selected]['portal_type']
        elif selected in self._addable_types():
            self.portal_type = selected.strip()
        else:
            raise KeyError("invalid workspace-type: %s", selected)

        self.title = title.strip()
        if self.portal_type in api.portal.get_tool('portal_types'):
            url = self.create()
            return self.redirect(url)

    def redirect(self, url):
        """
        Has its own method to allow overriding
        """
        url = '{}#workspace-settings'.format(url)
        return self.request.response.redirect(url)

    def get_new_object(self):
        ''' This will create a new object
        '''
        if self.request.form.get('workspace-type') \
           in self.all_templates_dict:
            return self.create_from_template()
        else:
            return super(AddWorkspace, self).get_new_object()

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

        new = api.content.copy(
            source=template,
            target=self.context,
            id=self.get_new_unique_id(),
            safe_id=False,
        )
        new.creation_date = datetime.now()
        return new

    def get_template(self):
        ''' Get a template to copy
        '''
        template_id = self.request.get('workspace-type')
        if not template_id:
            return
        # anyone trying to bypass this deserves an uncaught KeyError
        return self.allowed_templates[template_id]

    def update(self, obj):
        ''' Update the object and returns the modified fields and errors
        '''
        self.set_workspace_policy(obj)
        return super(AddWorkspace, self).update(obj)

    def set_workspace_policy(self, obj):
        ''' Set's the workspace policy for the objects given a scenario
        '''
        try:
            policy_id = self.request.form.get('workspace-type')
            policy = self.policies[policy_id]
        except KeyError:
            return

        purge_and_refresh_security_manager()

        obj.set_external_visibility(policy_id)  # yes this is the policy key
        obj.join_policy = policy['join_policy']
        obj.participant_policy = policy['participant_policy']
