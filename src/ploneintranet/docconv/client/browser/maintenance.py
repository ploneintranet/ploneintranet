# -*- coding: utf-8 -*-
from logging import getLogger
from ploneintranet import api as pi_api
from ploneintranet.async.browser.views import AbstractAsyncView
from ploneintranet.async.tasks import GeneratePreview
from ploneintranet.docconv.client import HTML_CONTENTTYPES
from ploneintranet.docconv.client import SUPPORTED_CONTENTTYPES
from ploneintranet.search.interfaces import ISiteSearch
from ploneintranet.search.solr.browser.maintenance import timer
from time import clock
from transaction import commit
from zope.annotation import IAnnotations
from zope.component import getUtility

logger = getLogger(__name__)


class BaseGeneratePreviewsView(AbstractAsyncView):
    ''' Helper View for maintenance tasks
    '''

    portal_types = SUPPORTED_CONTENTTYPES + HTML_CONTENTTYPES
    ADDITIONAL_PARAMETERS = [{'name': 'regenerate', 'type': 'checkbox'}]

    _preview_storage_key = 'collective.documentviewer'

    def clean_previews_for(self, obj):
        ''' Cleanup the previews for this object
        (useful if we want to regenerate the previews)
        '''
        IAnnotations(obj).pop(self._preview_storage_key, None)

    def generate_previews_for(self, obj):
        ''' By default don't do anything
        '''
        return

    def iter_objects(self):
        ''' Get the objects for which we want the previews to be regenerated
        '''
        write = self.request.response.write

        skip = int(self.request.get('skip', 0))
        if skip:
            write('skipping first %d object(s)...\n' % skip)

        regenerate = bool(self.request.get('regenerate'))
        if regenerate:
            write('forcing previews regeneration\n')

        search_util = getUtility(ISiteSearch)

        results = search_util.query(
            filters={
                'portal_type': self.portal_types,
                'path': '/'.join(self.context.getPhysicalPath())
            },
            start=skip,
            step=999999,
        )

        for result in results:
            obj = result.getObject()
            if regenerate:
                self.clean_previews_for(obj)
                yield obj
            elif not pi_api.previews.has_previews(obj):
                yield obj
            else:
                write('Skipping %r\n' % obj)

    def generate_previews(self):
        ''' Look for objects below this path and generate the previews
        '''
        write = self.request.response.write

        write('generating previews...\n')
        real = timer()          # real time
        cpu = timer(clock)      # cpu time

        processed = 0
        for obj in self.iter_objects():
            processed += 1
            write('Triggering preview generation for %r.\n' % obj)
            self.generate_previews_for(obj)

        write('previews generated.\n')
        msg = 'generated preview for %d items in %s (%s cpu time).' % (
            processed,
            real.next(),
            cpu.next()
        )
        write(msg)
        logger.info(msg)

    def __call__(self):
        ''' Generare previews in given context
        '''
        if self.authenticated():
            return self.generate_previews()
        else:
            return self.template()


class GenerateSyncPreviewsView(BaseGeneratePreviewsView):
    ''' Helper View for maintenance tasks '''

    def generate_previews_for(self, obj):
        ''' Generate the preview for this object and commit
        '''
        pi_api.previews.generate_previews(obj)
        commit()


class GeneratePreviewsAsyncView(BaseGeneratePreviewsView):
    ''' Helper View for maintenance tasks '''

    def generate_previews_for(self, obj):
        ''' Trigger the asynchronous preview generation for this object
        (if async previews are enabled)
        '''
        generator = GeneratePreview(obj, obj.REQUEST)
        generator(countdown=2)
