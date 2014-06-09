from rwproperty import getproperty, setproperty

from zope.interface import implements, alsoProvides
from zope.component import adapts

from plone.directives import form
from collective.gtags.field  import Tags

from Products.CMFCore.interfaces import IDublinCore

from collective.gtags import MessageFactory as _

class ISimpleSharing(form.Schema):
