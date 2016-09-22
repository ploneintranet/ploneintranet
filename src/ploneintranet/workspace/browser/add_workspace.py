# -*- coding: utf-8 -*-
from collections import defaultdict
from datetime import datetime
from plone import api
from plone.api.exc import InvalidParameterError
from plone.memoize.view import memoize
from ploneintranet import api as pi_api
from ploneintranet.core import ploneintranetCoreMessageFactory as _
from ploneintranet.workspace.browser.add_content import AddBase
from ploneintranet.workspace.config import TEMPLATES_FOLDER
from ploneintranet.workspace.subscribers import _reset_security_context
from ploneintranet.workspace.utils import purge_and_refresh_security_manager
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory
from logging import getLogger

vocab = 'ploneintranet.workspace.vocabularies.Divisions'
log = getLogger(__name__)


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
        """
        Addable but no template and not a default workspace.
        Uses unfiltered template list to ensure that only types that have
        no template at all are added to the menu.
        """
        _blocked = {
            x.portal_type
            for x in self.templates_folder.objectValues()
        }
        _blocked.add(self.default_fti)

        allowed_ftis = [
            fti for fti in self.context.allowedContentTypes()
            if fti.id not in _blocked
        ]
        return [
            {
                'id': fti.id,
                'portal_type': fti.id,
                'title': fti.title
            }
            for fti in allowed_ftis
        ]

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
        if not self.templates_folder:
            return {}
        return {brain.getId: brain.getObject()
                for brain in self.templates_folder.getFolderContents()
                if brain.getId not in self.policies}

    @property
    def templates_folder(self):
        portal = api.portal.get()
        return portal.get(self.TEMPLATES_FOLDER)

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
        ''' Create an object with the given template
        '''
        template = self.get_template()
        if not template:
            api.portal.show_message(
                _('Please specify which Case Template to use'),
                request=self.request,
                type="error",
            )
            return

        # Create neither previews for copied contents nor status updates.
        # Also, do not reindex copied content at this moment.
        pi_api.previews.events_disable(self.request)
        pi_api.microblog.events_disable(self.request)
        pi_api.events.disable_solr_indexing(self.request)
        new = api.content.copy(
            source=template,
            target=self.context,
            safe_id=False,
        )
        # We must not let api's `copy` method do the renaming. If the
        # acl_users folder is cached, then AccessControl checks will not
        # realise that the current user has the required permissions on
        # the copied template. We first need to invalidate the cache.
        # See https://github.com/quaive/ploneintranet/issues/727
        # and https://github.com/ploneintranet/ploneintranet/pull/438
        userid = api.user.get_current().id
        _reset_security_context(userid, new.REQUEST, invalidate_cache=True)
        # NOW we can set the new name
        api.content.rename(new, self.get_new_unique_id())
        new.creation_date = datetime.now()
        # Now that the new workspace has been created, re-index it (async)
        # using the solr-maintenance convenience method.
        pi_api.events.enable_solr_indexing(self.request)
        try:
            solr_maintenance = api.content.get_view(
                'solr-maintenance', new, self.request)
        except InvalidParameterError:
            log.warning('solr-maintenance view not available.')
        else:
            solr_maintenance.reindex(no_log=True)
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
        finally:
            purge_and_refresh_security_manager()

        obj.set_external_visibility(policy_id)  # yes this is the policy key
        obj.join_policy = policy['join_policy']
        obj.participant_policy = policy['participant_policy']
