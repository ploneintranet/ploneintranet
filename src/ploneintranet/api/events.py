# -*- coding: utf-8 -*-
# flake8: noqa
from ploneintranet.api.microblog import events_disable as disable_microblog
from ploneintranet.api.microblog import events_enable as enable_microblog
from ploneintranet.api.previews import events_disable as disable_previews
from ploneintranet.api.previews import events_enable as enable_previews

# not really event handlers themselves but provide a consistent API

def disable_solr_indexing(request=None):
    # avoid circular import deadlock by delaying import
    from ploneintranet.search.solr.indexers import solr_indexing_disable
    solr_indexing_disable(request)

def enable_solr_indexing(request=None):
    # avoid circular import deadlock by delaying import
    from ploneintranet.search.solr.indexers import solr_indexing_enable
    solr_indexing_enable(request)
