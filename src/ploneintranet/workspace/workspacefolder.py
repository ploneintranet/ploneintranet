from five import grok

#from z3c.form import group, field
#from zope import schema
#from zope.interface import invariant, Invalid
#from zope.schema.interfaces import IContextSourceBinder
#from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

from plone.dexterity.content import Container
#from plone.directives import dexterity
from plone.directives import form
#from plone.app.textfield import RichText
#from plone.namedfile.field import NamedImage, NamedFile
#from plone.namedfile.field import NamedBlobImage, NamedBlobFile
from plone.namedfile.interfaces import IImageScaleTraversable


#from ploneintranet.workspace import MessageFactory as _


# Interface class; used to define content-type schema.

class IWorkspaceFolder(form.Schema, IImageScaleTraversable):
    """
    A WorkspaceFolder users can collaborate in
    """

    # If you want a schema-defined interface, delete the model.load
    # line below and delete the matching file in the models sub-directory.
    # If you want a model-based interface, edit
    # models/workspace.xml to define the content type.

    form.model("models/workspacefolder.xml")


# Custom content-type class; objects created for this content type will
# be instances of this class. Use this class to add content-type specific
# methods and properties. Put methods that are mainly useful for rendering
# in separate view classes.

class WorkspaceFolder(Container):
    grok.implements(IWorkspaceFolder)

    # Add your class methods and properties here


# View class
# The view will automatically use a similarly named template in
# workspace_templates.
# Template filenames should be all lower case.
# The view will render when you request a content object with this
# interface with "/@@sampleview" appended.
# You may make this the default view for content objects
# of this type by uncommenting the grok.name line below or by
# changing the view class name and template filename to View / view.pt.

class SampleView(grok.View):
    """ sample view class """

    grok.context(IWorkspaceFolder)
    grok.require('zope2.View')

    # grok.name('view')

    # Add view methods here
