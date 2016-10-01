# -*- coding: utf-8 -*-
from plone import api
from plone.memoize.view import memoize
from plone.protect.authenticator import createToken
from ploneintranet.core import ploneintranetCoreMessageFactory as _
from ploneintranet.layout.browser.base import BaseView
from urllib import urlencode
from zope.annotation.interfaces import IAnnotations


class BaseArchiveView(BaseView):
    ''' The base class for the archiving story
    '''
    # BBB: should be 'slc: Toggle outdated',
    # but this is given to too many users
    archive_permission = 'Modify portal content'

    @property
    @memoize
    def can_archive(self):
        ''' Check if an object is outdated
        '''
        return api.user.has_permission(
            self.archive_permission,
            obj=self.context,
        )

    @property
    @memoize
    def is_archived(self):
        ''' Check if an object is outdated
        '''
        return IAnnotations(self.context).get('slc.outdated', False)

    def __call__(self):
        ''' Check if we have somethign to do before rendering the template
        '''
        if hasattr(self, 'action'):
            self.action()
        return super(BaseArchiveView, self).__call__()


class ArchiveView(BaseArchiveView):
    '''View to archive or unarchive an object
    '''
    notification_class = 'success'
    notification_msg = _(u'This item has been archived.')
    outdated = True

    def action(self):
        ''' Archive this document
        '''
        if self.can_archive:
            IAnnotations(self.context)['slc.outdated'] = self.outdated
            self.context.reindexObject(idxs=['outdated'])


class UnarchiveView(ArchiveView):
    '''View to archive or unarchive an object
    '''
    notification_class = 'warning'
    notification_msg = _(u'This item has been unarchived.')
    outdated = False


class ArchiveLinkIconified(BaseArchiveView):
    ''' A view that toggles the outdated status on this object
    '''
    base_css_class = 'icon iconified pat-inject icon-archive'

    @property
    def query_options(self):
        ''' The query string options for the bookmark action
        '''
        options = {
            '_authenticator': createToken(),
        }
        return options

    @property
    def query_string(self):
        ''' The urlencoded query string options for the bookmark action
        '''
        return urlencode(self.query_options)

    def maybe_disable_diazo(self):
        ''' No need to disable diazo for this one
        '''
        return False

    @property
    def link_options(self):
        ''' Get the link options
        '''
        if self.is_archived:
            options = {
                'action': '@@unarchive',
                'title': _('Unarchive this document'),
                'css_class': 'active',
                'label': _('Unarchive'),
            }
        else:
            options = {
                'action': '@@archive',
                'title': _('Archive this document'),
                'css_class': '',
                'label': _('Archive'),
            }
        return options
