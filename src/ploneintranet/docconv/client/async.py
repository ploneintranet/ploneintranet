import pytz
from datetime import datetime, timedelta
from logging import getLogger
from time import strftime
from StringIO import StringIO

from DateTime import DateTime
from PIL import Image
from Products.CMFCore.interfaces import ISiteRoot
from Products.Five import BrowserView
from plone.app.async.interfaces import IAsyncService
from plone.app.async.service import (
    _executeAsUser,
    _getAuthenticatedUser,
    job_success_callback,
    job_failure_callback,
)
from zc.async.job import Job
from zope.annotation import IAnnotations
from zope.component import getUtility
from zope.component.interfaces import ComponentLookupError

from ploneintranet.docconv.client.config import (
    ASYNC_CONVERSION_DELAY,
    PDF_VERSION_KEY,
    PREVIEW_IMAGES_KEY,
    THUMBNAIL_KEY,
    DOCCONV_EXCLUDE_TYPES as EXCLUDE_TYPES,
)
from ploneintranet.docconv.client.fetcher import fetchPreviews

logger = getLogger(__name__)


def queueConversionJob(context, request=None, force=False):
    if request is None:
        request = context.REQUEST
    try:
        async = getUtility(IAsyncService)
        queues = async.getQueues()
    except KeyError, e:
        logger.warn('KeyError: %s' % e)
        return
    except ComponentLookupError, e:
        logger.warn('ComponentLookupError: %s' % e)
        return
    queue = queues.get('', None)
    path = context.getPhysicalPath()
    if force or path not in [j.args[0] for j in queue if len(j.args) >= 6
                             and j.args[4] == fetchPreviews]:
        virtual_url_parts = request.get('VIRTUAL_URL_PARTS')
        vr_path = list(request.get('VirtualRootPhysicalPath', ()))
        async.queueJob(fetchPreviews, context, virtual_url_parts, vr_path)
        return True
    return False


def queueDelayedConversionJob(context, request):
    """ queue a delayed fetchPreview if none queued yet. If already queued
    reset the delay by removing current job(s) and queueing a new delayed
    one """
    try:
        async = getUtility(IAsyncService)
        queues = async.getQueues()
    except KeyError:
        return
    except ComponentLookupError, e:
        logger.warn('ComponentLookupError: %s' % e)
        return
    # I consider that dangerous because the queue is already in process.
    # Modifying it in addition may call for conflicts
    queue = queues.get('', None)
#    path = context.getPhysicalPath()
#    my_jobs = [j for j in queue if len(j.args) >= 6
#                               and j.args[4] == fetchPreviews
#                               and j.args[0] == path]
#    if my_jobs:
#        for j in my_jobs:
#            queue.remove(j)

    virtual_url_parts = context.REQUEST.get('VIRTUAL_URL_PARTS')
    vr_path = list(request.get('VirtualRootPhysicalPath', ()))

    portal = getUtility(ISiteRoot)
    portal_path = portal.getPhysicalPath()
    context_path = context.getPhysicalPath()
    uf_path, user_id = _getAuthenticatedUser()

    job = Job(_executeAsUser, context_path, portal_path, uf_path, user_id,
              fetchPreviews, virtual_url_parts, vr_path)
    # job = async.queueJob(fetchPreviews, self.context,
    #     virtual_url_parts, vr_path)
    job = queue.put(job, begin_after=datetime.now(pytz.UTC) + timedelta(0,
                    ASYNC_CONVERSION_DELAY))
    job.addCallbacks(success=job_success_callback,
                     failure=job_failure_callback)
    return True


class RecursiveQueueJob(BrowserView):
    """ Queues docconv jobs for the context and everything inside. Default
        behaviour:

        * skip if type is in EXCLUDE_TYPES
        * skip if object already has preview/thumb images

        URL Parameters:

        * *dryrun*:
           don't really queue jobs, just show what would be done

        * *force*:
           overwrite existing previews/thumbs

        * *minresolution*:
           overwrite if existing previews are smaller than this

        * *modified*:
          only consider objects modified after this date, or between these
          dates if a tuple/list is given (not even counted as skipped)

        Examples:

        *queue all objects modified after 1.12., even if they have previews*

        /@@convertall?force=true&modified=20121201T00:00:00%2B00:00


        *show which objects have previews with a resolution lower than
        1024x768 (or none at all)*

        /@@convertall?dryrun=true&minresolution:int:tuple=1024&
        minresolution:int:tuple=768

        *or, synonymous:*

        /@@convertall?dryrun=true&minresolution=1024x768


        *queue objects modified between 1. and 2.12. that have a lower
        x resolution than 1024*

        /@@convertall?modified:tuple=20121201T00:00:00%2B00:00&
        modified:tuple=20121202T00:00:00%2B00:00& minresolution:int=1024
        """

    def mklog(self, use_std_log=False):
        """ helper to prepend a time stamp to the output """
        write = self.request.RESPONSE.write

        def log(msg, timestamp=True):
            if timestamp:
                msg = strftime('%Y/%m/%d-%H:%M:%S ') + msg
            write(msg)
            if use_std_log:
                logger.info(msg)
        return log

    def get_force(self):
        ''' Check if the object is the object is force
        '''
        force = self.request.get('force', False)
        if isinstance(force, basestring):
            return self.force in ('True', 'true')
        return force

    def get_modified(self):
        ''' Get a modified parameter for a query to portal_catalog
        '''
        modified = self.request.get('modified')
        if not modified:
            return

        if isinstance(modified, (list, tuple)):
            if len(modified) == 1:
                modified = modified[0]
            elif len(modified) == 2:
                modified_range = tuple([DateTime(m) for m in modified])
                return dict(query=modified_range, range='min:max')

        if isinstance(modified, basestring):
            return dict(query=DateTime(modified), range='min')

    def get_minresolution(self):
        ''' Get a modified parameter for a query to portal_catalog
        '''
        minresolution = self.request.get('minresolution')
        if isinstance(minresolution, basestring):
            minresolution = tuple(r or '0' for r in minresolution.split('x'))
        if isinstance(minresolution, (list, tuple)):
            # consider just the first two
            minresolution = tuple(map(int, minresolution[:2]))
        return minresolution

    def hasPreviews(self, obj):
        return all(
            IAnnotations(obj).get(PDF_VERSION_KEY) is not None,
            IAnnotations(obj).get(PREVIEW_IMAGES_KEY) is not None,
            IAnnotations(obj).get(THUMBNAIL_KEY) is not None,
        )

    def low_resolution(self, obj):
        minresolution = self.get_minresolution()
        if not minresolution:
            return False
        for imgdata in IAnnotations(obj).get(PREVIEW_IMAGES_KEY):
            if Image.open(StringIO(imgdata)).size < minresolution:
                return True
        return False

    def get_candidates(self):
        log = self.mklog(use_std_log=True)
        query = dict(path=['/'.join(self.context.getPhysicalPath())])
        if self.modified:
            query['modified'] = self.modified
        brains = self.context.portal_catalog(query)
        objs = []
        for brain in brains:
            try:
                objs.append(brain.getObject())
            except:
                log('Could not get object %s\n' % brain.getPath())
                continue
        return objs

    def queable(self, obj):
        ''' State if obj is queable
        '''
        if not (
            (
                hasattr(obj.aq_explicit, 'getContentType')
                and not obj.getContentType().split('/')[0] in EXCLUDE_TYPES
            )
            or hasattr(obj.aq_explicit, 'text')
        ):
            return False
        if not (
            self.force
            or not self.hasPreviews(obj)
            or self.low_resolution(obj)
        ):
            return False
        return True

    def has_excluded_content_type(self, obj):
        ''' State if obj is skippable
        '''
        return (
            hasattr(obj.aq_explicit, 'getContentType')
            and obj.getContentType().split('/')[0] in EXCLUDE_TYPES
        )

    def queue(self, obj):
        ''' Queue obj
        '''
        if not self.dryrun:
            queueConversionJob(obj, self.request, force=self.force)

        moreinfo = dict(hasPreviews=self.hasPreviews(obj))
        if moreinfo['hasPreviews']:
            moreinfo['low_resolution'] = self.low_resolution(obj)
            if moreinfo['low_resolution']:
                imgdata = StringIO(
                    IAnnotations(obj).get(PREVIEW_IMAGES_KEY)[-1])
                size = Image.open(imgdata).size
                moreinfo['current_resolution'] = size
        msg = 'Queued  %s (%s)\n' % ('/'.join(obj.getPhysicalPath()), moreinfo)
        self.log(msg)
        self.queued += 1

    def skip(self, obj):
        ''' Skip object
        '''
        if self.has_excluded_content_type(obj):
            moreinfo = 'type "{0}" excluded'.format(
                obj.getContentType().split('/')[0]
            )
        elif not hasattr(obj.aq_explicit, 'text'):
            moreinfo = 'no getContentType or text'
        else:
            moreinfo = dict(hasPreviews=self.hasPreviews(obj))
            if moreinfo['hasPreviews']:
                moreinfo['low_resolution'] = self.low_resolution(obj)
        self.log('Skipped {0} ({1})\n'.format(
            '/'.join(obj.getPhysicalPath()), moreinfo))
        self.skipped += 1

    def render(self):
        self.log = self.mklog(use_std_log=True)
        self.dryrun = self.request.get('dryrun', False)
        self.force = self.get_force()

        try:
            self.modified = self.get_modified()
        except:
            self.modified = None
            self.log('Could not convert modified to DateTime')
            return

        self.queued = 0
        self.skipped = 0

        candidates = self.get_candidates()
        for obj in candidates:
            if self.queable(obj):
                self.queue(obj)
            else:
                self.skip(obj)

        msg = (
            'Queued Docconv jobs for %d objects, skipped %d, modified '
            'range %s, resolution threshold %s\n'
        ) % (
            self.queued,
            self.skipped,
            self.modified,
            self.get_minresolution()
        )
        self.log(msg)
        if self.dryrun:
            self.log('Dry run, no jobs actually queued\n')
