# coding=utf-8
from plone.indexer.decorator import indexer

from .behaviors import INewsMeta


@indexer(INewsMeta)
def section_uuid(obj, **kw):
    return obj.section.to_object.uuid
